from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from debug import log_error_and_capture_screenshot

from fonction import FonctionRepeat


class AffranchigoForfaitCase:
    def __init__(self, driver):
        self.driver = driver
        # Cas Onglet
        self.fonction_repeat = FonctionRepeat(driver)

    def is_select_value_present(self, select_selector):
        """Vérifie si un élément select a une valeur sélectionnée."""
        try:
            select_element = Select(
                self.driver.find_element(By.CSS_SELECTOR, select_selector)
            )
            return select_element.first_selected_option.text.strip() != ""
        except NoSuchElementException:
            return False

    def is_specific_option_selected(self, select_selector, option_text):
        """Vérifie si une option spécifique est sélectionnée dans un élément select."""
        try:
            select_element = Select(
                self.driver.find_element(By.CSS_SELECTOR, select_selector)
            )
            selected_option_text = select_element.first_selected_option.text.strip()
            return selected_option_text == option_text
        except NoSuchElementException:
            print(f"Selecteur '{select_selector}' non trouvé.")
            return False

    # Fonction pour selectionner l'Heure dans le cas
    def select_time_in_selectors(self):
        select_time_selectors = [
            "#g0_p159\\|0_r486\\[0\\] > div > critere-form:nth-child(5) > div.form-group.critere_psc > input-component > div.no-left-gutter.has-success.col-xs-8.col-sm-8.col-md-8 > select",
            "#\\[g0_p159\\|0_r486\\[0\\]\\] > div > critere-form:nth-child(5) > div.form-group.critere_psc > input-component > div.no-left-gutter.col-xs-8.col-sm-8.col-md-8 > select",
            "#g0_p159\\|0_r486\\[0\\] > div > critere-form:nth-child(7) > div.form-group.critere_psc > input-component > div.no-left-gutter.has-success.col-xs-8.col-sm-8.col-md-8 > select",
            "#\\[g0_p159\\|0_r486\\[0\\]\\] > div > critere-form:nth-child(7) > div.form-group.critere_psc > input-component > div.no-left-gutter.col-xs-8.col-sm-8.col-md-8 > select",
        ]

        for select_time_selector in select_time_selectors:
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, select_time_selector)
                    )
                )
                select_element = Select(
                    self.driver.find_element(By.CSS_SELECTOR, select_time_selector)
                )

                # Obtenir la valeur actuelle sélectionnée
                current_value = select_element.first_selected_option.get_attribute('value')
                print(f"Valeur actuelle sélectionnée pour {select_time_selector}: '{current_value}'")

                # Vérifier si une heure n'est pas sélectionnée ou si la valeur est 'null'
                if current_value in ['', 'null']:
                    print(f"Aucune heure sélectionnée ou valeur 'null' pour {select_time_selector}. Sélection de l'heure par défaut.")
                    select_element.select_by_index(16)
                else:
                    print(f"L'heure est déjà sélectionnée pour {select_time_selector}: '{current_value}'.")

            except TimeoutException:
                print(f"Selecteur '{select_time_selector}' non trouvé.")
            except Exception as e:
                print(f"Erreur lors de la sélection de l'heure pour {select_time_selector}: {e}")

    def handle_case_1(self, driver):
        print("Début de handle_case_1")
        # Initialisation des variables
        traitement_present = False
        depot_present = False
        # Les sélecteurs des deux premiers 'select'
        select_1_selector = "#g0_p159\\|0_r486\\[0\\] > div > critere-form:nth-child(3) > div.form-group.critere_psc > input-etb-prest > div > select"
        select_2_selector = "#\\[g0_p159\\|0_r486\\[0\\]\\] > div > critere-form:nth-child(3) > div.form-group.critere_psc > input-etb-prest > div > select"

        try:
            select_1 = Select(
                self.driver.find_element(By.CSS_SELECTOR, select_1_selector)
            )
            print("Selecteur 1 trouvé avec succès.")
            select_2 = Select(
                self.driver.find_element(By.CSS_SELECTOR, select_2_selector)
            )
            print("Selecteur 2 trouvé avec succès.")

            driver.save_screenshot("debug_selecteurs.png")

            # Vérification des options dans les sélecteurs
            print(f"Nombre d'options dans select_1: {len(select_1.options)}")
            print(f"Nombre d'options dans select_2: {len(select_2.options)}")

            # Définir les sélecteurs pour 'Traitement' et 'Dépôt'
            traitement_select_selector = "#g0_p159\\|0_r486\\[0\\] > div > critere-form:nth-child(9) > div.form-group.critere_psc > input-component > div > select"
            depot_select_selector = "#\\[g0_p159\\|0_r486\\[0\\]\\] > div > critere-form:nth-child(9) > div.form-group.critere_psc > input-component > div > select"

            if len(select_1.options) == 2 and len(select_2.options) == 2:
                traitement_present = self.is_specific_option_selected(
                    traitement_select_selector, "Traitement"
                ) or self.is_specific_option_selected(
                    depot_select_selector, "Traitement"
                )
                depot_present = self.is_specific_option_selected(
                    traitement_select_selector, "Dépôt"
                ) or self.is_specific_option_selected(depot_select_selector, "Dépôt")
                print(
                    f"Traitement présent: {traitement_present}, Dépôt présent: {depot_present}"
                )

            if traitement_present and depot_present:
                self.select_time_in_selectors()
                
                print("Cas 1 satisfait")
                driver.save_screenshot("debug_cas_1_satisfait.png")
            else:
                print("Conditions pour le Cas 1 non remplies")
                driver.save_screenshot("debug_cas_1_non_remplies.png")

        except NoSuchElementException as e:
            print(f"Erreur cas 1 : {e}")
            log_error_and_capture_screenshot(driver, "Forfait_Cas_1", e)

    def handle_case_2(self, driver):
        print("Début de handle_case_2")
        # Selecteurs Rôles
        select_1_role = "#g0_p159\\|0_r486\\[0\\] > div > critere-form:nth-child(9) > div.form-group.critere_psc > input-component > div > select"
        select_2_role = "#\\[g0_p159\\|0_r486\[0\\]\\] > div > critere-form:nth-child(9) > div.form-group.critere_psc > input-component > div > select"
    
        try:
            select_first_role = Select(driver.find_element(By.CSS_SELECTOR, select_1_role))
            select_second_role = Select(driver.find_element(By.CSS_SELECTOR, select_2_role))
            # Vérifie les selecteurs role
            if select_first_role.first_selected_option.text == "Dépôt" and select_second_role.first_selected_option.text == "Dépôt et Traitement":
                select_element = Select(
                    driver.find_element(By.CSS_SELECTOR, select_2_role)
                )
                select_element.select_by_index(2)

            elif select_first_role.first_selected_option.text == "" and select_second_role.first_selected_option.text == "Dépôt":
                select_element = Select(
                    driver.find_element(By.CSS_SELECTOR, select_1_role)
                )
                select_element.select_by_index(2)

            elif select_first_role.first_selected_option.text == "Dépôt" and select_second_role.first_selected_option.text == "":
                select_element = Select(
                    driver.find_element(By.CSS_SELECTOR, select_2_role)
                )
                select_element.select_by_index(2)
            else:
                print("Ne conviens pas au cas Liberté 2")
            # Selectionne l'heure
            self.select_time_in_selectors()
            print("L'heure c'est bien mis a jour")
        except NoSuchElementException as e:
            print(f"Erreur Cas Forfait 2 : {e}")
            log_error_and_capture_screenshot(driver, "Forfait_Case_2", e)

    def handle_case_3(self, driver):
        print("Début de handle_case_3")
        """
        Traite le cas où l'option "Dépôt et Traitement" est sélectionnée.
        """
        # Sélecteur pour 'Dépôt et Traitement'
        depot_traitement_selector = "#g0_p159\\|0_r486\\[0\\] > div > critere-form:nth-child(9) > div.form-group.critere_psc > input-component > div > select"

        try:
            # Vérifie si "Dépôt et Traitement" est sélectionné
            depot_traitement_present = self.is_specific_option_selected(
                depot_traitement_selector, "Dépôt et Traitement"
            )
            print(f"Dépôt et Traitement présent: {depot_traitement_present}")

            if depot_traitement_present:
                # Appel de la fonction pour l'heure si "Dépôt et Traitement" est sélectionné
                self.select_time_in_selectors()
                print("Cas 3 ('Dépôt et Traitement') satisfait")
            else:
                print("Condition pour le Cas 3 ('Dépôt et Traitement') non remplie")
                log_error_and_capture_screenshot(driver, "Condition non remplis pour le forfait cas 3", e)

        except NoSuchElementException as e:
            print(f"Erreur dans handle_case_3 ('Dépôt et Traitement') : {e}")
            log_error_and_capture_screenshot(driver, "Forfait_Cas_3", e)
