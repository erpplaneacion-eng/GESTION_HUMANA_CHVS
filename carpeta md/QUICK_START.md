# ⚡ Inicio Rápido - Gestión Humana CAVJP

**Para desarrolladores que quieren empezar YA**

---

## 🚀 En 3 Pasos

### 1️⃣ Ejecutar Script

```bash
# En Linux/Mac/WSL:
./start_local.sh

# En Windows:
start_local.bat
```

### 2️⃣ Abrir Navegador

```
http://localhost:8000
```

### 3️⃣ Empezar a Desarrollar

**¡Listo!** El sistema está corriendo en local.

---

## 📍 Rutas Importantes

| URL | Descripción |
|-----|-------------|
| http://localhost:8000/formapp/registro/ | Formulario público |
| http://localhost:8000/formapp/lista/ | Lista de candidatos (requiere login) |
| http://localhost:8000/admin/ | Panel Django Admin |
| http://localhost:8000/login/ | Iniciar sesión |

---

## 👤 Crear Usuario Admin (Primera vez)

Si necesitas acceder al panel administrativo:

```bash
cd gestion_humana
python manage.py createsuperuser
```

Ingresa:
- **Username**: tu_usuario
- **Email**: tu@email.com
- **Password**: (mínimo 8 caracteres)

---

## 🛑 Detener el Servidor

Presiona `Ctrl + C` en la terminal donde está corriendo.

---

## 📚 ¿Necesitas más información?

- **Desarrollo Local Completo**: Ver [README_LOCAL.md](README_LOCAL.md)
- **Diferencias Local vs Producción**: Ver [ENVIRONMENTS.md](ENVIRONMENTS.md)
- **Configuración Detallada**: Ver [DUAL_ENVIRONMENT_SETUP.md](DUAL_ENVIRONMENT_SETUP.md)
- **Descripción del Proyecto**: Ver [README.md](README.md)

---

## ⚠️ Problemas?

### Error: "comando no encontrado"

**Linux/Mac/WSL:**
```bash
chmod +x start_local.sh
./start_local.sh
```

**Windows:**
- Ejecutar desde CMD o PowerShell como administrador

### Error: "No module named 'django'"

```bash
# Activar entorno virtual manualmente
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate.bat  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Intentar de nuevo
cd gestion_humana
python manage.py runserver
```

### Puerto 8000 ocupado

```bash
# Usar otro puerto
python manage.py runserver 8080
```

---

**¿Listo para empezar?** 🎉

```bash
./start_local.sh
```