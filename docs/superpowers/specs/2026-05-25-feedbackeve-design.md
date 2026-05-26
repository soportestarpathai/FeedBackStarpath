# FeedbackEve — Design Spec
**Fecha:** 2026-05-25
**Stack:** Django 5 + MySQL + HTMX + Alpine.js + TailwindCSS + WeasyPrint

---

## Objetivo

Portal unificado de calidad e incidencias para centralizar el reporte de errores, quejas y sugerencias de todas las plataformas de la empresa (EVE 360, Órbita, Medical y futuros proyectos). Reemplaza los reportes individuales por un sistema único donde testers y usuarios reportan desde un mismo sitio, y el Admin gestiona, filtra y exporta los casos en PDF.

---

## Roles

| Rol | Acceso |
|-----|--------|
| **Usuario** | Registro abierto. Formulario simplificado (título, descripción, tipo, severidad, screenshots). Solo ve sus propios reportes. Solo puede reportar en plataformas que el Admin le haya asignado. |
| **Tester** | Creado por Admin. Formulario completo con campos técnicos. Ve todos los reportes. Puede cambiar el estado de cualquier reporte. |
| **Admin** | Creado por Admin. Acceso total: gestiona plataformas, usuarios, estados y genera PDFs. |

Implementado con Django Groups + decoradores de permiso.

---

## Arquitectura

**Enfoque:** Django Monolito (MVT) con HTMX para interacciones dinámicas y Alpine.js para comportamiento en cliente. Un solo proyecto, sin frontend separado.

```
feedbackeve/
├── config/              ← settings, urls, wsgi
├── apps/
│   ├── accounts/        ← login, registro, gestión de usuarios y roles
│   ├── platforms/       ← CRUD de plataformas (Admin)
│   ├── reports/         ← reportes, formularios, detalle, historial
│   └── exports/         ← generación de PDFs con WeasyPrint
├── templates/
│   ├── base.html        ← layout principal (navbar + sidebar)
│   ├── partials/        ← fragmentos HTMX (tabla, filtros, modal)
│   └── pdf/             ← templates para WeasyPrint
├── static/
│   ├── css/             ← TailwindCSS (compilado)
│   └── js/              ← Alpine.js
└── manage.py
```

---

## Modelos de Datos

### `accounts.User` (extiende AbstractUser)
| Campo | Tipo | Notas |
|-------|------|-------|
| email | EmailField | único, usado para login |
| nombre | CharField | |
| rol | CharField | choices: USUARIO, TESTER, ADMIN |
| plataformas_asignadas | M2M → Platform | solo aplica al rol Usuario: limita en qué plataformas puede crear reportes; Tester/Admin no tienen restricción |
| creado_en | DateTimeField | auto |

### `platforms.Platform`
| Campo | Tipo | Notas |
|-------|------|-------|
| nombre | CharField | ej. "EVE 360" |
| descripcion | TextField | opcional |
| color | CharField | hex, para el badge en UI |
| activa | BooleanField | default True |
| creado_en | DateTimeField | auto |

### `reports.Report`
| Campo | Tipo | Notas |
|-------|------|-------|
| titulo | CharField | |
| descripcion | TextField | |
| plataforma | FK → Platform | |
| tipo | CharField | BUG, SUGERENCIA, QUEJA |
| severidad | CharField | BAJA, MEDIA, ALTA, CRITICA |
| estado | CharField | ABIERTO, EN_REVISION, RESUELTO, CERRADO |
| url_pagina | URLField | opcional |
| pasos_reproducir | TextField | solo visible/requerido para Tester+ |
| resultado_esperado | TextField | solo Tester+ |
| resultado_obtenido | TextField | solo Tester+ |
| entorno | JSONField | navegador, OS, resolución |
| reportado_por | FK → User | |
| creado_en | DateTimeField | auto |
| actualizado_en | DateTimeField | auto |

### `reports.Screenshot`
| Campo | Tipo | Notas |
|-------|------|-------|
| reporte | FK → Report | on_delete=CASCADE |
| imagen | ImageField | subida a MEDIA_ROOT |
| subido_en | DateTimeField | auto |

### `reports.StatusHistory`
| Campo | Tipo | Notas |
|-------|------|-------|
| reporte | FK → Report | on_delete=CASCADE |
| estado_anterior | CharField | |
| estado_nuevo | CharField | |
| cambiado_por | FK → User | |
| fecha | DateTimeField | auto |

---

## Páginas y Vistas

### Auth
| URL | Vista | Acceso |
|-----|-------|--------|
| `/login/` | Formulario login | Público |
| `/registro/` | Registro (rol Usuario) | Público |
| `/logout/` | Cerrar sesión | Autenticado |

### General
| URL | Vista | Acceso |
|-----|-------|--------|
| `/` | Dashboard: stats + tabla con filtros HTMX. Usuario ve solo sus reportes; Tester/Admin ven todos. | Autenticado |
| `/reportes/nuevo/` | Formulario nuevo reporte (simple o completo según rol) | Autenticado |
| `/reportes/<id>/` | Detalle: campos, screenshots, historial de estados | Autenticado |

### Admin
| URL | Vista | Acceso |
|-----|-------|--------|
| `/admin/plataformas/` | CRUD de plataformas | Admin |
| `/admin/usuarios/` | Lista + cambio de roles | Admin |
| `/admin/reportes/` | Todos los reportes + cambio de estado inline | Admin / Tester |
| `/exports/pdf/` | Formulario de filtros + descarga PDF | Admin |

---

## HTMX — Interacciones Dinámicas

| Acción | Trigger | Target |
|--------|---------|--------|
| Filtrar tabla por plataforma/tipo/estado/severidad | `hx-get` en chips | `#tabla-reportes` |
| Buscar reportes por título | `hx-get` con debounce | `#tabla-reportes` |
| Cambiar estado de reporte | `hx-patch` en select | fila de la tabla |
| Abrir modal nuevo reporte | `hx-get` | `#modal` |
| Subir imagen (preview) | Alpine.js | preview inline |

---

## Exportación PDF

- Ruta: `GET /exports/pdf/?plataforma=&estado=&severidad=&desde=&hasta=`
- WeasyPrint renderiza un template HTML dedicado (`templates/pdf/reporte.html`)
- El PDF incluye:
  - Encabezado con logo y datos del filtro aplicado
  - Tabla de reportes agrupada por estado o severidad
  - Sección de totales (total por tipo, por severidad)
  - Screenshots embebidas como imágenes en base64
- Respuesta: `Content-Disposition: attachment; filename="reporte-eve360-2026-05-25.pdf"`

---

## Estilos

- **Paleta principal:** Navy `#0a1628` / `#0f2044`, Accent `#0ea5e9`
- **Fondo:** `#f0f4f8`, Cards blancas con borde `#e2e8f0`
- **Severidades:** Crítico=rojo, Alta=naranja, Media=amarillo, Baja=verde
- **Estado:** Abierto=rojo, En revisión=amarillo, Resuelto=verde, Cerrado=gris
- Referencia visual: mockup en `mockup.html` (raíz del proyecto)

---

## Fuera de Alcance (v1)

- Notificaciones por email
- API REST pública
- Integración con plataformas externas (webhooks)
- App móvil
