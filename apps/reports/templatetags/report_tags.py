from django import template
from django.utils.safestring import mark_safe

register = template.Library()

_TIPO_STYLE = {
    'BUG':        ('background:#fee2e2;color:#dc2626',  'Bug'),
    'SUGERENCIA': ('background:#fef9c3;color:#ca8a04',  'Sugerencia'),
    'QUEJA':      ('background:#fce7f3;color:#db2777',  'Queja'),
}
_SEV_STYLE = {
    'CRITICA': ('background:#4c0519;color:#fecdd3', 'Crítica'),
    'ALTA':    ('background:#fef2f2;color:#dc2626', 'Alta'),
    'MEDIA':   ('background:#fff7ed;color:#ea580c', 'Media'),
    'BAJA':    ('background:#f0fdf4;color:#16a34a', 'Baja'),
}
_ESTADO_DOT = {
    'ABIERTO':     ('#2563eb', 'Abierto'),
    'EN_REVISION': ('#d97706', 'En Revisión'),
    'RESUELTO':    ('#059669', 'Resuelto'),
    'CERRADO':     ('#94a3b8', 'Cerrado'),
}

@register.simple_tag
def badge_tipo(tipo):
    style, label = _TIPO_STYLE.get(tipo, ('background:#f1f5f9;color:#64748b', tipo))
    return mark_safe(f'<span class="text-xs font-medium px-2 py-0.5 rounded-full" style="{style};">{label}</span>')

@register.simple_tag
def badge_severidad(sev):
    style, label = _SEV_STYLE.get(sev, ('background:#f1f5f9;color:#64748b', sev))
    return mark_safe(f'<span class="text-xs font-semibold px-2 py-0.5 rounded-full" style="{style};">{label}</span>')

@register.simple_tag
def dot_estado(estado):
    color, _ = _ESTADO_DOT.get(estado, ('#94a3b8', estado))
    return mark_safe(f'<span class="w-2 h-2 rounded-full flex-shrink-0 inline-block" style="background:{color};"></span>')

@register.simple_tag
def label_estado(estado):
    _, label = _ESTADO_DOT.get(estado, ('#94a3b8', estado))
    return label
