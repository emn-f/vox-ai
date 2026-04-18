@echo off
chcp 65001 >nul

echo 🏳️‍🌈 PROJETO VOX AI 🏳️‍🌈
echo Execução de Supabase Migration (develop -^> main)
echo.

:: 1. Verificando se o Docker está rodando
echo [INFO] Verificando status do Docker...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo 🚫 [ERRO] O Docker não está rodando. Abra o Docker Desktop e tente novamente...
    pause
    goto op2
)

echo Docker em execução ✅
echo.

echo Informe o diretório do Projeto Vox no seu computador, sem aspas:
set /p local="> "

:: 2. Verificando se o diretório existe
if not exist "%local%\" (
    echo 🚫 [ERRO] O diretório informado não existe.
    pause
    goto op2
)

cd /d "%local%"

echo.
echo Informe a descrição da migration referente aos ultimos ajustes realizados no banco (sem espacos, use_underscores).
echo ℹ️ Se tiver dúvidas, consulte https://github.com/emn-f/vox-ai/blob/main/docs/CONVENTIONAL_MIGRATIONS.md
set /p desc="> "

:: 3. Linkando no Supabase e Autenticando o DB
echo.
echo 🔒 O Supabase precisa da senha do banco de ^>HOMOLOGAÇÃO^< para ler o schema remoto. Digite a senha abaixo:
set /p SUPABASE_DB_PASSWORD="> "

echo.
echo [INFO] Linkando no Supabase...
supabase link --project-ref baolyrgupanfceyuzhkj
if %errorlevel% neq 0 (
    echo 🚫 [ERRO] Falha ao linkar com o Supabase. Verifique se o projeto na nuvem esta pausado.
    pause
    goto op2
)

echo.
echo [INFO] Gerando Migration...
supabase db diff --linked --use-migra -f "%desc%"
if %errorlevel% neq 0 (
    echo 🚫 [ERRO] Ocorreu um problema ao gerar a migration.
    pause
    goto op2
)

:: 4. Buscando o arquivo gerado
echo.
echo [INFO] Localizando arquivo gerado na pasta supabase\migrations...
set "migration_file="

for /f "delims=" %%I in ('dir "supabase\migrations\*_%desc%.sql" /b /o-d 2^>nul') do (
    set "migration_file=supabase\migrations\%%I"
    goto :verificar_migration
)

:verificar_migration
:: 5. EXCEÇÃO: Tratativa para MIGRATION VAZIA ou SEM ALTERAÇÕES
if not defined migration_file (
    echo.
    echo ⚠️ [AVISO] Nenhum arquivo gerado. Isso significa que NAO HOUVE ALTERACOES de schema para migrar!
    pause
    goto op2
)

:: Verifica se o arquivo foi criado, mas tem 0 bytes de tamanho
for %%F in ("%migration_file%") do set tamanho=%%~zF
if %tamanho% EQU 0 (
    echo.
    echo ⚠️ [AVISO] O arquivo foi gerado, mas esta VAZIO (0 bytes). Nenhuma alteracao detectada!
    echo 🗑️ Apagando arquivo inútil...
    del "%migration_file%"
    pause
    goto op2
)

:: (O bloco 6 de abrir o arquivo foi removido daqui)

echo.
echo [SUCESSO] Migration gerada com exito! ✅
echo [INFO] O arquivo foi salvo em: %migration_file%
echo.

echo [INFO] Parando containers do Supabase...
:: Mudei para supabase stop para garantir que ele mate todos os servicos da porta 54320 sem sujar a tela
supabase stop >nul 2>&1

goto op2

:op2
echo.
echo Encerrando rotina...
echo 🤖 Vox AI: conversas que importam 🏳️‍🌈
echo.
:: O cmd /k segura a janela aberta no final ao invés de fechar na sua cara
cmd /k