import uvicorn
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

if __name__ == "__main__":
    # Configurações do servidor
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    reload = os.getenv("DEBUG", "True").lower() == "true"
    
    print(f"Iniciando servidor em http://{host}:{port}")
    print("Pressione CTRL+C para parar o servidor")
    
    # Inicia o servidor
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload
    ) 