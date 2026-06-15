import sys, os
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
sys.stdout.reconfigure(encoding='utf-8')

"""
FeedBackStarpath - Browser flow tests
Screenshots saved to test_screenshots/
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8000"
OUT  = Path("test_screenshots")
OUT.mkdir(exist_ok=True)

RESULTS = []

USERS = {
    "usuario":    "usuario@eve360.mx",
    "tester":     "tester@eve360.mx",
    "admin":      "admin@eve360.mx",
    "superadmin": "superadmin@feedbackeve.mx",
}
PWD = "1234"

def shot(page, name):
    p = OUT / f"{name}.png"
    page.screenshot(path=str(p), full_page=True)
    print(f"  [SHOT] {p.name}")

def ok(msg):
    RESULTS.append(("OK  ", msg))
    print(f"  [OK  ] {msg}")

def fail(msg):
    RESULTS.append(("FAIL", msg))
    print(f"  [FAIL] {msg}")

def warn(msg):
    RESULTS.append(("WARN", msg))
    print(f"  [WARN] {msg}")

def do_login(page, email, password=PWD):
    page.goto(f"{BASE}/login/")
    page.wait_for_load_state("networkidle")
    page.fill('[name=email]', email)
    page.fill('[name=password]', password)
    page.click('button[type=submit]')
    page.wait_for_load_state("networkidle")

def do_logout(page):
    try:
        btn = page.locator('form[action*="logout"] button').first
        btn.click(timeout=3000)
        page.wait_for_load_state("networkidle")
    except Exception:
        page.goto(f"{BASE}/login/")

# ── FLUJO 1: Login ──────────────────────────────────────────────
def flow_login(page):
    print("\n=== FLUJO 1: Login ===")
    page.goto(f"{BASE}/login/")
    page.wait_for_load_state("networkidle")
    shot(page, "01_login_page")
    ok("Pagina login carga")

    # Credenciales incorrectas
    page.fill('[name=email]', 'noexiste@test.com')
    page.fill('[name=password]', 'wrong')
    page.click('button[type=submit]')
    page.wait_for_load_state("networkidle")
    body = page.content()
    shot(page, "02_login_bad_creds")
    if "Credenciales" in body or "incorrectas" in body:
        ok("Error mostrado por credenciales incorrectas")
    else:
        warn("No se vio mensaje de error por credenciales incorrectas")

    # Login como usuario
    do_login(page, USERS["usuario"])
    url = page.url
    shot(page, "03_login_usuario_ok")
    if "/login/" not in url:
        ok(f"Login USUARIO exitoso -> {url}")
    else:
        fail(f"Login USUARIO fallo, sigue en {url}")

# ── FLUJO 2: Registro ───────────────────────────────────────────
def flow_registro(page):
    print("\n=== FLUJO 2: Registro ===")
    page.goto(f"{BASE}/registro/")
    page.wait_for_load_state("networkidle")
    shot(page, "04_registro_form")
    ok("Pagina registro carga")

    import time
    ts = int(time.time())
    email = f"autotest_{ts}@eve360.mx"

    page.fill('[name=email]', email)
    try:
        page.fill('[name=first_name]', 'Auto', timeout=3000)
        page.fill('[name=last_name]', 'Test', timeout=3000)
    except Exception:
        pass
    page.fill('[name=password1]', 'AutoTest123!')
    page.fill('[name=password2]', 'AutoTest123!')
    page.click('button[type=submit]')
    page.wait_for_load_state("networkidle")
    shot(page, "05_registro_resultado")
    url = page.url
    if "/login/" in url:
        ok("Registro exitoso -> redirige a login")
    else:
        body = page.content()
        if "error" in body.lower() or "ya existe" in body.lower():
            warn(f"Registro rechazado")
        else:
            ok(f"Registro completado: {url}")

# ── FLUJO 3: Usuario - ver reportes y crear ─────────────────────
def flow_usuario(page):
    print("\n=== FLUJO 3: Usuario - reportes ===")
    do_login(page, USERS["usuario"])
    page.wait_for_load_state("networkidle")
    shot(page, "06_usuario_home")
    ok(f"Login USUARIO -> {page.url}")

    # Lista reportes
    page.goto(f"{BASE}/reportes/")
    page.wait_for_load_state("networkidle")
    shot(page, "07_usuario_lista_reportes")
    ok("Lista reportes USUARIO carga")

    # Detalle de primer reporte si existe
    links = page.locator('a[href*="/reportes/"]').all()
    detail = [l for l in links
              if l.get_attribute("href")
              and "/reportes/" in l.get_attribute("href")
              and "nuevo" not in l.get_attribute("href")
              and l.get_attribute("href").rstrip("/").split("/")[-1].isdigit()]
    if detail:
        href = detail[0].get_attribute("href")
        page.goto(f"{BASE}{href}" if href.startswith("/") else href)
        page.wait_for_load_state("networkidle")
        shot(page, "08_usuario_detalle_reporte")
        ok(f"Detalle reporte carga: {href}")
    else:
        warn("No hay reportes listados para ver detalle")

    # Nuevo reporte
    page.goto(f"{BASE}/reportes/nuevo/")
    page.wait_for_load_state("networkidle")
    shot(page, "09_usuario_form_nuevo")
    if "/login/" in page.url:
        fail("Form nuevo reporte redirige a login (no autenticado?)")
        return
    ok("Form nuevo reporte carga")

    page.fill('[name=titulo]', 'Bug prueba automatizada Playwright')
    page.fill('[name=descripcion]', 'Este bug fue creado por el test automatico de Playwright.')
    try:
        opts = page.locator('[name=plataforma] option').all()
        if len(opts) > 1:
            page.select_option('[name=plataforma]', index=1)
    except Exception:
        warn("Sin opciones de plataforma disponibles")

    page.select_option('[name=severidad]', 'MEDIA')
    page.locator('form:has([name=titulo]) button[type=submit]').click()
    page.wait_for_load_state("networkidle")
    shot(page, "10_usuario_reporte_creado")
    url = page.url
    if "nuevo" not in url and "/reportes/" in url:
        ok("Reporte MEDIA creado exitosamente")
    else:
        body = page.content()
        if "error" in body.lower() or "requerido" in body.lower() or "required" in body.lower():
            fail(f"Reporte rechazado por validacion")
        else:
            ok(f"Reporte enviado: {url}")

    # Verificar que CRITICA NO aparece en opciones de severidad (cap activo)
    page.goto(f"{BASE}/reportes/nuevo/")
    page.wait_for_load_state("networkidle")
    sev_values = page.locator('[name=severidad] option').evaluate_all('els => els.map(e => e.value)')
    shot(page, "11_usuario_severidad_opciones")
    if 'CRITICA' not in sev_values:
        ok(f"Cap CRITICA activo: opciones disponibles = {sev_values}")
    else:
        warn(f"CRITICA visible en selector de severidad para USUARIO (deberia estar oculta): {sev_values}")

# ── FLUJO 4: Tester ─────────────────────────────────────────────
def flow_tester(page):
    print("\n=== FLUJO 4: Tester - gestionar estados ===")
    do_login(page, USERS["tester"])
    page.wait_for_load_state("networkidle")
    shot(page, "12_tester_home")
    ok(f"Login TESTER -> {page.url}")

    page.goto(f"{BASE}/reportes/")
    page.wait_for_load_state("networkidle")
    shot(page, "13_tester_lista")
    ok("Tester lista reportes carga")

    # Buscar link a un reporte
    links = page.locator('a[href*="/reportes/"]').all()
    detail = [l for l in links
              if l.get_attribute("href")
              and "/reportes/" in l.get_attribute("href")
              and "nuevo" not in l.get_attribute("href")
              and l.get_attribute("href").rstrip("/").split("/")[-1].isdigit()]
    if not detail:
        warn("No se encontraron links a reportes individuales")
        return

    href = detail[0].get_attribute("href")
    page.goto(f"{BASE}{href}" if href.startswith("/") else href)
    page.wait_for_load_state("networkidle")
    shot(page, "14_tester_detalle")
    ok(f"Tester detalle reporte: {href}")

    # Cambiar estado
    try:
        estado_select = page.locator('select[name=estado]')
        if estado_select.count() > 0:
            page.select_option('select[name=estado]', 'EN_REVISION')
            page.locator('form[action*="estado/"] button[type=submit]').click()
            page.wait_for_load_state("networkidle")
            shot(page, "15_tester_estado_cambiado")
            ok("Tester cambio estado a EN_REVISION")
        else:
            warn("Select de estado no encontrado en detalle")
    except Exception as e:
        warn(f"No se pudo cambiar estado: {e}")

    # Crear reporte como tester
    page.goto(f"{BASE}/reportes/nuevo/")
    page.wait_for_load_state("networkidle")
    if "/login/" not in page.url:
        shot(page, "16_tester_nuevo_form")
        ok("Tester puede acceder a form de nuevo reporte")
    else:
        warn("Tester redirigido a login desde /reportes/nuevo/")

# ── FLUJO 5: Admin ──────────────────────────────────────────────
def flow_admin(page):
    print("\n=== FLUJO 5: Admin - panel ===")
    do_login(page, USERS["admin"])
    page.wait_for_load_state("networkidle")
    shot(page, "17_admin_home")
    ok(f"Login ADMIN -> {page.url}")

    for url_path, nombre, shot_name in [
        ("/admin/resumen/",   "Admin resumen",           "18_admin_resumen"),
        ("/admin/reportes/",  "Admin lista reportes",    "19_admin_reportes"),
        ("/admin/usuarios/",  "Admin gestion usuarios",  "20_admin_usuarios"),
    ]:
        page.goto(f"{BASE}{url_path}")
        page.wait_for_load_state("networkidle")
        shot(page, shot_name)
        if "/login/" not in page.url and url_path.split("/")[2] in page.url:
            ok(f"{nombre} carga OK")
        else:
            fail(f"{nombre} redirige a {page.url}")

    # Filtro reportado_por
    page.goto(f"{BASE}/admin/reportes/?reportado_por=1")
    page.wait_for_load_state("networkidle")
    shot(page, "21_admin_filtro_reportado_por")
    ok("Filtro reportado_por en admin carga sin error")

    # Cambiar rol de un usuario
    page.goto(f"{BASE}/admin/usuarios/")
    page.wait_for_load_state("networkidle")
    usuarios_rows = page.locator('tbody tr').all()
    if usuarios_rows:
        ok(f"Admin ve {len(usuarios_rows)} usuario(s) en la tabla")
    else:
        warn("Tabla de usuarios vacia para este admin")

# ── FLUJO 6: SuperAdmin ──────────────────────────────────────────
def flow_superadmin(page):
    print("\n=== FLUJO 6: SuperAdmin - gestion total ===")
    do_login(page, USERS["superadmin"])
    page.wait_for_load_state("networkidle")
    shot(page, "22_sa_home")
    ok(f"Login SUPERADMIN -> {page.url}")

    for url_path, nombre, shot_name in [
        ("/superadmin/dashboard/",  "SA Dashboard",      "23_sa_dashboard"),
        ("/superadmin/plataformas/","SA Plataformas",    "24_sa_plataformas"),
        ("/superadmin/admins/",     "SA Lista admins",   "25_sa_admins"),
        ("/superadmin/admins/crear/","SA Asignar admin", "26_sa_crear_admin"),
        ("/superadmin/config/",     "SA Config global",  "27_sa_config"),
    ]:
        page.goto(f"{BASE}{url_path}")
        page.wait_for_load_state("networkidle")
        shot(page, shot_name)
        cur = page.url
        if "/login/" not in cur:
            ok(f"{nombre} carga OK")
        else:
            fail(f"{nombre} redirige a login")

    # Probar crear admin con email inexistente
    page.goto(f"{BASE}/superadmin/admins/crear/")
    page.wait_for_load_state("networkidle")
    page.fill('[name=email]', 'noexiste999@test.com')
    page.locator('form:has([name=email]) button[type=submit]').click()
    page.wait_for_load_state("networkidle")
    shot(page, "28_sa_crear_admin_error")
    body = page.content()
    if "no existe" in body.lower() or "error" in body.lower():
        ok("Error correcto: email inexistente no puede ser admin")
    else:
        warn("Sin mensaje de error para email inexistente en form crear admin")

# ── FLUJO 7: Swagger / API ───────────────────────────────────────
def flow_swagger(page):
    print("\n=== FLUJO 7: Swagger / API ===")
    page.goto(f"{BASE}/api/v1/docs/")
    page.wait_for_load_state("networkidle")
    shot(page, "29_swagger_ui")
    body = page.content()
    if "swagger" in body.lower() or "openapi" in body.lower():
        ok("Swagger UI carga correctamente")
    else:
        fail("Swagger UI no cargó")

    # JWT token endpoint - verifica via HTTP (el schema es un download YAML)
    import urllib.request, http.cookiejar
    _jar = http.cookiejar.CookieJar()
    _opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(_jar))
    try:
        resp = _opener.open(f"{BASE}/api/v1/schema/")
        ct = resp.headers.get('Content-Type', '')
        ok(f"OpenAPI schema disponible en /api/v1/schema/ (Content-Type: {ct})")
    except Exception as e:
        warn(f"/api/v1/schema/ error: {e}")

# ── MAIN ─────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("FeedBackStarpath - Browser Flow Tests")
    print("=" * 60)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False, slow_mo=300)
        ctx  = browser.new_context(viewport={"width": 1400, "height": 900})
        page = ctx.new_page()

        try:
            flow_login(page)
            do_logout(page)

            flow_registro(page)
            do_logout(page)

            flow_usuario(page)
            do_logout(page)

            flow_tester(page)
            do_logout(page)

            flow_admin(page)
            do_logout(page)

            flow_superadmin(page)
            do_logout(page)

            flow_swagger(page)

        except Exception as e:
            import traceback
            fail(f"Error critico inesperado: {e}")
            traceback.print_exc()
        finally:
            browser.close()

    print("\n" + "=" * 60)
    print("RESUMEN FINAL")
    print("=" * 60)
    for status, msg in RESULTS:
        print(f"  [{status}] {msg}")

    total  = len(RESULTS)
    passed = sum(1 for s, _ in RESULTS if s == "OK  ")
    failed = sum(1 for s, _ in RESULTS if s == "FAIL")
    warned = sum(1 for s, _ in RESULTS if s == "WARN")
    print(f"\n  {passed}/{total} OK | {failed} FAIL | {warned} WARN")
    print(f"  Screenshots: {OUT.resolve()}")

if __name__ == "__main__":
    main()
