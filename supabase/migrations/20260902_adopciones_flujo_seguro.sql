begin;

alter table public.adopcion
    add column if not exists adoptante_id integer references public.usuario(usuario_id_pk),
    add column if not exists contacto_responsable text,
    add column if not exists contacto_adoptante text;

alter table public.adopcion_postulacion
    add column if not exists contacto text;

-- Copia el contacto de respuestas historicas a su columna privada. Las respuestas
-- originales se conservan como respaldo; el backend las redacta de listados y ranking.
update public.adopcion_postulacion p
set contacto = (
    select r.respuesta_texto
    from public.adopcion_respuesta r
    join public.adopcion_pregunta q on q.pregunta_id = r.pregunta_id_fk
    where r.postulacion_id_fk = p.postulacion_id
      and lower(q.texto) like '%medio de contacto%'
    order by r.respuesta_id desc
    limit 1
)
where p.contacto is null
  and exists (
      select 1
      from public.adopcion_respuesta r
      join public.adopcion_pregunta q on q.pregunta_id = r.pregunta_id_fk
      where r.postulacion_id_fk = p.postulacion_id
        and lower(q.texto) like '%medio de contacto%'
  );

-- Los cierres del flujo anterior no guardaban los contactos necesarios. Se
-- reabren para evitar representar como completas adopciones incompletas.
update public.adopcion set estado = 'activa' where estado = 'cerrada';
update public.adopcion_postulacion
set estado = 'pendiente'
where estado in ('aprobada', 'aprobado', 'en_evaluacion');

alter table public.adopcion alter column estado set default 'activa';
alter table public.adopcion_postulacion alter column estado set default 'pendiente';

alter table public.adopcion
    add constraint adopcion_estado_valido
        check (estado in ('activa', 'completada')),
    add constraint adopcion_completada_coherente
        check (
            (estado = 'activa' and adoptante_id is null
                and contacto_responsable is null and contacto_adoptante is null)
            or
            (estado = 'completada' and adoptante_id is not null
                and nullif(btrim(contacto_responsable), '') is not null
                and nullif(btrim(contacto_adoptante), '') is not null)
        );

alter table public.adopcion_postulacion
    add constraint adopcion_postulacion_estado_valido
        check (estado in ('pendiente', 'aceptada', 'rechazada'));

create unique index if not exists adopcion_postulacion_usuario_unica
    on public.adopcion_postulacion(adopcion_id_fk, usuario_id_fk);
create unique index if not exists adopcion_una_postulacion_aceptada
    on public.adopcion_postulacion(adopcion_id_fk)
    where estado = 'aceptada';

create or replace function public.aprobar_postulacion_adopcion(
    p_adopcion_id bigint,
    p_postulacion_id bigint,
    p_responsable_id bigint,
    p_contacto_responsable text
) returns jsonb
language plpgsql
set search_path = public
as $$
declare
    v_adopcion public.adopcion%rowtype;
    v_postulacion public.adopcion_postulacion%rowtype;
    v_rechazada record;
begin
    select * into v_adopcion
    from public.adopcion
    where adopcion_id = p_adopcion_id
    for update;

    if not found then
        raise exception 'No se encontro la adopcion' using errcode = 'P0002';
    end if;
    if v_adopcion.usuario_id_fk <> p_responsable_id then
        raise exception 'No puedes aprobar postulaciones de una adopcion ajena'
            using errcode = '42501';
    end if;
    if v_adopcion.estado <> 'activa' then
        raise exception 'La adopcion ya fue completada' using errcode = '23514';
    end if;
    if nullif(btrim(p_contacto_responsable), '') is null then
        raise exception 'El contacto del responsable es obligatorio'
            using errcode = '23514';
    end if;

    select * into v_postulacion
    from public.adopcion_postulacion
    where postulacion_id = p_postulacion_id
      and adopcion_id_fk = p_adopcion_id
    for update;

    if not found then
        raise exception 'La postulacion no pertenece a esta adopcion'
            using errcode = 'P0002';
    end if;
    if v_postulacion.estado <> 'pendiente' then
        raise exception 'La postulacion ya fue resuelta' using errcode = '23514';
    end if;
    if nullif(btrim(v_postulacion.contacto), '') is null then
        raise exception 'La postulacion seleccionada no tiene contacto'
            using errcode = '23514';
    end if;

    update public.adopcion_postulacion
    set estado = case
        when postulacion_id = p_postulacion_id then 'aceptada'
        else 'rechazada'
    end
    where adopcion_id_fk = p_adopcion_id;

    update public.adopcion
    set estado = 'completada',
        adoptante_id = v_postulacion.usuario_id_fk,
        contacto_responsable = btrim(p_contacto_responsable),
        contacto_adoptante = btrim(v_postulacion.contacto)
    where adopcion_id = p_adopcion_id;

    insert into public.notificaciones(usuario_id, tipo, titulo, mensaje, data)
    values (
        v_postulacion.usuario_id_fk,
        'adopcion_aceptada',
        'Tu postulacion fue aceptada',
        'Fuiste seleccionado para adoptar. Ya puedes contactar al responsable.',
        jsonb_build_object(
            'adopcion_id', p_adopcion_id,
            'postulacion_id', p_postulacion_id,
            'contacto_responsable', btrim(p_contacto_responsable)
        )
    );

    for v_rechazada in
        select postulacion_id, usuario_id_fk
        from public.adopcion_postulacion
        where adopcion_id_fk = p_adopcion_id
          and postulacion_id <> p_postulacion_id
    loop
        insert into public.notificaciones(usuario_id, tipo, titulo, mensaje, data)
        values (
            v_rechazada.usuario_id_fk,
            'adopcion_rechazada',
            'La adopcion selecciono a otra persona',
            'Gracias por postularte. En esta ocasion se selecciono a otra persona.',
            jsonb_build_object(
                'adopcion_id', p_adopcion_id,
                'postulacion_id', v_rechazada.postulacion_id
            )
        );
    end loop;

    return jsonb_build_object(
        'message', 'Postulacion aceptada y adopcion completada.',
        'adopcion_id', p_adopcion_id,
        'postulacion_id', p_postulacion_id,
        'adoptante_id', v_postulacion.usuario_id_fk,
        'estado', 'completada'
    );
end;
$$;

-- El backend usa service_role. Impedir que clientes Supabase invoquen la RPC
-- directamente evita que suplanten p_responsable_id fuera de FastAPI.
revoke all on function public.aprobar_postulacion_adopcion(bigint, bigint, bigint, text)
    from public, anon, authenticated;
grant execute on function public.aprobar_postulacion_adopcion(bigint, bigint, bigint, text)
    to service_role;

commit;
