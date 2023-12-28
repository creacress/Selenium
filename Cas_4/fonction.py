from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException, ElementNotInteractableException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from debug import log_error_and_capture_screenshot

class FonctionRepeat:

    def __init__(self, driver):
        self.driver = driver
    
    def action_particuliere(self):
        print("Début de action_particuliere")
        # Clique sur "Conditions Particulières de Réalisations"
        try:
            h1_element = self.driver.find_element(By.TAG_NAME, "h1")
            self.driver.execute_script("arguments[0].scrollIntoView();", h1_element)
            element = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "#content_offre > ul > li:nth-child(3) > a")
                )
            )
            element.click()
            print("Le clique à bien été effectué")
        except (TimeoutException, NoSuchElementException, Exception) as e:
            log_error_and_capture_screenshot(self.driver, "Onglet Conditions Particulières de ventes non trouvé ou cliquable", e)
        
        # Tentative de sélection d'heure de relevage
        try:
            select_heures_depot = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "#p159CPR > critere-form > div.form-group.critere_psc > input-component > div > select")
                )
            )
            select_heures_depot = Select(select_heures_depot)

            # Sélectionner l'heure si aucune heure n'est actuellement sélectionnée
            if select_heures_depot.first_selected_option.get_attribute('value') == '':
                select_heures_depot.select_by_index(3)
                print("Une nouvelle heure a été sélectionnée.")
            else:
                print("Une heure est déjà sélectionnée, aucune action supplémentaire n'est requise.")
            
        except NoSuchElementException as e:
            print(f"Erreur : Le select pour les heures de dépôt est introuvable. {e}")
            log_error_and_capture_screenshot(self.driver, "Heure de relevages non trouvés", e)
        except ElementNotInteractableException as e:
            print(f"Erreur : Impossible d'interagir avec le select pour les heures de dépôt. {e}")
            log_error_and_capture_screenshot(self.driver, "Intéractions avec Heure de relevages impossibles", e)
        except Exception as e:
            print(f"Erreur inattendue lors de la manipulation du select pour les heures de dépôt : {e}")
            log_error_and_capture_screenshot(self.driver, "Erreur inattendue avec la manipulation", e)
