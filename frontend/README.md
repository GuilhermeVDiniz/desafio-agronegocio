# Fronteed - Dashboard Agronegócio

Um dashboard web simples para visualização de dados de produção de culturas por mesorregião geográfica no Brasil.

## Requisitos
 - Browser
 - Docker

---

## 🐳 Executando o Frontend (sem backend)
O Dockerfile usa a imagem **BusyBox** com um servidor HTTP simples embutido.

### Execução Local

```bash
# Build da imagem
  docker build -t dashboard-frontend .

# Executar container
  docker run -p 3000:3000 dashboard-frontend
```
👉 Agora acesse no navegador:
http://localhost:3000