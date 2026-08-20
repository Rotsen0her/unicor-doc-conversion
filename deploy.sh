#!/bin/bash

# Script de despliegue automático para Ubuntu Server
# unicor-doc-conversion — servicio de conversión PDF/Office -> Markdown

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "\n${BLUE}============================================================${NC}"
echo -e "${BLUE}🚀 DESPLIEGUE unicor-doc-conversion${NC}"
echo -e "${BLUE}============================================================${NC}\n"

# ==========================================
# 1. Verificar .env
# ==========================================
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  Archivo .env no encontrado${NC}"

    if [ -f .env.example ]; then
        echo -e "${BLUE}📝 Creando .env desde .env.example...${NC}"
        cp .env.example .env
        echo -e "${GREEN}✅ Archivo .env creado${NC}"
        echo -e "${YELLOW}⚠️  IMPORTANTE: edita .env con un INTERNAL_API_KEY real antes de continuar${NC}"
        echo -e "\n${BLUE}Comandos sugeridos:${NC}"
        echo -e "  python3 -c \"import secrets; print(secrets.token_hex(32))\"   # generar la clave"
        echo -e "  nano .env    # pegarla en INTERNAL_API_KEY"
        echo -e "  ./deploy.sh  # volver a ejecutar este script"
        exit 1
    else
        echo -e "${RED}❌ No se encontró .env.example${NC}"
        exit 1
    fi
fi

# ==========================================
# 2. Verificar configuración mínima
# ==========================================
echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}🔍 VERIFICANDO CONFIGURACIÓN${NC}"
echo -e "${BLUE}============================================================${NC}\n"

# INTERNAL_API_KEY es lo único realmente obligatorio acá — sin ella el
# servicio queda abierto (modo inseguro explícito, ver app/auth.py).
INTERNAL_KEY_VALUE=$(grep -E "^INTERNAL_API_KEY=" .env | cut -d '=' -f2-)
if [ -z "$INTERNAL_KEY_VALUE" ]; then
    echo -e "${RED}❌ INTERNAL_API_KEY vacía en .env — el servicio quedaría sin autenticar${NC}"
    echo -e "${YELLOW}   Genera una con: python3 -c \"import secrets; print(secrets.token_hex(32))\"${NC}"
    read -p "¿Continuar de todos modos, sin autenticación? (s/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        echo -e "${RED}❌ Despliegue cancelado${NC}"
        exit 1
    fi
elif [[ "$INTERNAL_KEY_VALUE" == *"CAMBIA_ESTO"* ]]; then
    echo -e "${RED}❌ INTERNAL_API_KEY sigue con el valor de ejemplo del .env.example${NC}"
    echo -e "${YELLOW}   Cualquiera con la key por defecto podría llamar al servicio.${NC}"
    read -p "¿Continuar de todos modos? (s/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        echo -e "${RED}❌ Despliegue cancelado${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ INTERNAL_API_KEY configurada${NC}"
fi

echo -e "${YELLOW}ℹ️  Recuerda: la misma INTERNAL_API_KEY debe estar en CONVERSION_SERVICE_KEY del .env de backend_web_bot.${NC}"

# ==========================================
# 3. Detener contenedores anteriores
# ==========================================
echo -e "\n${BLUE}============================================================${NC}"
echo -e "${BLUE}🛑 DETENIENDO CONTENEDORES ANTERIORES${NC}"
echo -e "${BLUE}============================================================${NC}\n"

if docker compose ps | grep -q "Up"; then
    echo -e "${BLUE}Deteniendo contenedores...${NC}"
    docker compose down
    echo -e "${GREEN}✅ Contenedores detenidos${NC}"
else
    echo -e "${YELLOW}⚠️  No hay contenedores ejecutándose${NC}"
fi

# ==========================================
# 4. Construir imagen Docker
# ==========================================
echo -e "\n${BLUE}============================================================${NC}"
echo -e "${BLUE}🐋 CONSTRUYENDO IMAGEN DOCKER${NC}"
echo -e "${BLUE}============================================================${NC}\n"
echo -e "${YELLOW}ℹ️  Docling trae PyTorch — la primera build puede tardar varios${NC}"
echo -e "${YELLOW}   minutos (build cacheada después). Es normal.${NC}\n"

if docker compose build; then
    echo -e "\n${GREEN}✅ Imagen construida exitosamente${NC}"
else
    echo -e "\n${RED}❌ Error construyendo imagen Docker${NC}"
    exit 1
fi

# ==========================================
# 5. Iniciar contenedor
# ==========================================
echo -e "\n${BLUE}============================================================${NC}"
echo -e "${BLUE}🚀 INICIANDO CONTENEDOR${NC}"
echo -e "${BLUE}============================================================${NC}\n"
echo -e "${YELLOW}ℹ️  Este compose crea la red net-shared-conversion. Si${NC}"
echo -e "${YELLOW}   backend_web_bot ya está arriba y la esperaba como externa,${NC}"
echo -e "${YELLOW}   puede hacer falta un 'docker compose up -d' de ese lado también.${NC}\n"

if docker compose up -d; then
    echo -e "\n${GREEN}✅ Contenedor iniciado${NC}"
else
    echo -e "\n${RED}❌ Error iniciando contenedor${NC}"
    exit 1
fi

# ==========================================
# 6. Esperar inicio del servicio
# ==========================================
echo -e "\n${BLUE}============================================================${NC}"
echo -e "${BLUE}⏳ ESPERANDO INICIO DEL SERVICIO${NC}"
echo -e "${BLUE}============================================================${NC}\n"

echo -e "${BLUE}Esperando 15 segundos...${NC}"
sleep 15

# ==========================================
# 7. Verificar estado
# ==========================================
echo -e "\n${BLUE}============================================================${NC}"
echo -e "${BLUE}🏥 VERIFICANDO ESTADO DEL SERVICIO${NC}"
echo -e "${BLUE}============================================================${NC}\n"

echo -e "${BLUE}Estado del contenedor:${NC}"
docker compose ps

echo -e "\n${BLUE}Últimos logs:${NC}"
docker compose logs --tail=30

# ==========================================
# 8. Test de health check
# ==========================================
echo -e "\n${BLUE}============================================================${NC}"
echo -e "${BLUE}🩺 TEST DE HEALTH CHECK${NC}"
echo -e "${BLUE}============================================================${NC}\n"

if command -v curl &> /dev/null; then
    sleep 5
    if curl -f http://localhost:8100/health &> /dev/null; then
        echo -e "${GREEN}✅ Health check exitoso — servicio respondiendo${NC}"
    else
        echo -e "${YELLOW}⚠️  Health check falló — el servicio puede estar iniciando${NC}"
        echo -e "${YELLOW}   Espera unos segundos y verifica: curl http://localhost:8100/health${NC}"
    fi

    if [ -n "$INTERNAL_KEY_VALUE" ]; then
        echo -e "\n${BLUE}Probando /v1/engines con la key configurada...${NC}"
        if curl -sf -H "X-Internal-Key: $INTERNAL_KEY_VALUE" http://localhost:8100/v1/engines > /dev/null; then
            echo -e "${GREEN}✅ /v1/engines responde con la key correcta${NC}"
        else
            echo -e "${YELLOW}⚠️  /v1/engines no respondió como se esperaba — revisar logs${NC}"
        fi
    fi
else
    echo -e "${YELLOW}⚠️  curl no instalado — saltando test${NC}"
fi

# ==========================================
# 9. Resumen final
# ==========================================
echo -e "\n${BLUE}============================================================${NC}"
echo -e "${GREEN}🎉 DESPLIEGUE COMPLETADO${NC}"
echo -e "${BLUE}============================================================${NC}\n"

echo -e "${BLUE}📍 URLs disponibles:${NC}"
echo -e "   • Servicio:         http://$(hostname -I | awk '{print $1}'):8100"
echo -e "   • Health Check:     http://$(hostname -I | awk '{print $1}'):8100/health"

echo -e "\n${BLUE}📊 Comandos útiles:${NC}"
echo -e "   • Ver logs:         docker compose logs -f"
echo -e "   • Reiniciar:        docker compose restart"
echo -e "   • Detener:          docker compose down"
echo -e "   • Estado:           docker compose ps"
echo -e "   • Entrar al cont.:  docker compose exec conversion bash"

echo -e "\n${BLUE}🔧 Verificar que funciona:${NC}"
echo -e "   curl http://localhost:8100/health"
echo -e "   curl -H \"X-Internal-Key: <tu key>\" http://localhost:8100/v1/engines"

echo -e "\n${YELLOW}📌 Pendiente en backend_web_bot:${NC}"
echo -e "   Configura CONVERSION_SERVICE_URL=http://<esta-ip-o-hostname>:8100"
echo -e "   y CONVERSION_SERVICE_KEY=<la misma INTERNAL_API_KEY> en su .env."

echo -e "\n${GREEN}✅ unicor-doc-conversion desplegado y listo para recibir peticiones${NC}\n"

exit 0
