import logging
from logging.handlers import RotatingFileHandler
import datetime
from selenium import webdriver
import os

# Configuration du Logger
def setup_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.ERROR)
    logger.propagate = False  # Empêche la propagation au logger parent

    handler = RotatingFileHandler('error.log', maxBytes=5000000, backupCount=5)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S.%f')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

# Fonction pour enregistrer les erreurs et capturer les screenshots
def log_error_and_capture_screenshot(driver: webdriver, contrat_numero, error):
    logger = setup_logger()
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_file = f"screenshots/error_{contrat_numero}_{timestamp}.png"
    
    if not os.path.exists('screenshots'):
        os.makedirs('screenshots')
    driver.save_screenshot(screenshot_file)

    # Enregistre l'erreur dans le log avec le chemin du screenshot
    logger.error(f"Erreur dans le contrat numéro {contrat_numero}: {error}, Screenshot: {screenshot_file}")
