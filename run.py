from app import create_app
from waitress import serve
import logging
from urllib.parse import urljoin

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = create_app()

def list_routes():
    base_url = "http://localhost:5000"
    logger.info("\n" + "="*50)
    logger.info("Available endpoints:")
    logger.info("="*50)
    
    for rule in app.url_map.iter_rules():
        methods = ','.join(sorted(rule.methods - {'OPTIONS', 'HEAD'}))
        url = urljoin(base_url, str(rule))
        logger.info(f"Endpoint: {rule.endpoint}")
        logger.info(f"Methods: {methods}")
        logger.info(f"URL: {url}")
        logger.info("-"*50)
    
    # Thêm các URL đặc biệt
    logger.info("Special URLs:")
    logger.info(f"Swagger UI: {base_url}/api/docs")
    logger.info("="*50 + "\n")

if __name__ == '__main__':
    list_routes()
    logger.info("Server is starting...")
    logger.info("Press Ctrl+C to quit")
    serve(app, host='0.0.0.0', port=5000) 