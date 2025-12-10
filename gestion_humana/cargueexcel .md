PS C:\Users\User\OneDrive\Desktop\CAVIJUP\GESTION_HUMANA_CHVS> & C:/Users/User/OneDrive/Desktop/CAVIJUP/GESTION_HUMANA_CHVS/venv/Scripts/Activate.ps1
(venv) PS C:\Users\User\OneDrive\Desktop\CAVIJUP\GESTION_HUMANA_CHVS> railway login  
> Open the browser? Yes
Logged in as chvs (erp.planeacion@vallesolidario.com)                                                                   
(venv) PS C:\Users\User\OneDrive\Desktop\CAVIJUP\GESTION_HUMANA_CHVS> railway link
> Select a workspace chvs app proyectos
> Select a project gestion humana
> Select an environment production
> Select a service <esc to skip> Postgres_gestion_humana

Project gestion humana linked successfully! 🎉
(venv) PS C:\Users\User\OneDrive\Desktop\CAVIJUP\GESTION_HUMANA_CHVS> railway run python manage.py cargar_historico
python: can't open file 'C:\\Users\\User\\OneDrive\\Desktop\\CAVIJUP\\GESTION_HUMANA_CHVS\\manage.py': [Errno 2] No such file or directory
(venv) PS C:\Users\User\OneDrive\Desktop\CAVIJUP\GESTION_HUMANA_CHVS> cd .\gestion_humana\
(venv) PS C:\Users\User\OneDrive\Desktop\CAVIJUP\GESTION_HUMANA_CHVS\gestion_humana> railway run python manage.py cargar_historico
Iniciando carga desde C:\Users\User\OneDrive\Desktop\CAVIJUP\GESTION_HUMANA_CHVS\gestion_humana\basedatosaquicali\management\commands\..\..\archivos_excel\link.xlsx...
CommandError: Ocurrió un error durante la carga de datos: could not translate host name "postgres.railway.internal" to address: Name or service not known
(venv) PS C:\Users\User\OneDrive\Desktop\CAVIJUP\GESTION_HUMANA_CHVS\gestion_humana> 