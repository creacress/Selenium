import os
import json
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException

# Charge les variables d'env si nécessaire 
load_dotenv()

# Accéder aux variables 
identifiant = os.getenv('IDENTIFIANT')
mot_de_passe = os.getenv('MOT_DE_PASSE')
web_site = os.getenv('WEB_SITE')
url_redirection = os.getenv('URL_REDIRECTION')

def configure_selenium():
    print("Configuration de Selenium...")
    service = Service("data/msedgedriver.exe")
    driver = webdriver.Edge(service=service)
    driver.get(
        web_site
    )
    wait = WebDriverWait(driver, 5)
    return driver, wait


def login(wait):
    print("Tentative de connexion...")
    
    try:
        input_identifiant = wait.until(
            EC.presence_of_element_located((By.ID, "AUTHENTICATION.LOGIN"))
        )
        input_identifiant.clear()
        input_identifiant.send_keys(identifiant)

        input_mot_de_passe = wait.until(
            EC.presence_of_element_located((By.ID, "AUTHENTICATION.PASSWORD"))
        )
        input_mot_de_passe.clear()
        input_mot_de_passe.send_keys(mot_de_passe)
        input_mot_de_passe.send_keys(Keys.RETURN)
    except TimeoutException:
        print("Déjà connecté ou le champ d'identifiant n'est pas présent.")


def process_json_files():
    print("Traitement du fichier JSON pour le cas 4...")
    numeros_contrat = []

    file_path = "data/cas_4.json"
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            data = json.load(file)
            for value in data.values():
                numeros_contrat.append(value)

    return numeros_contrat


def submit_contract_number(wait, numero):
    print(f"Soumission du numéro de contrat {numero}...")
    input_element = wait.until(EC.presence_of_element_located((By.ID, "idContrat")))
    input_element.clear()
    input_element.send_keys(numero)
    input_element.send_keys(Keys.RETURN)

    submit_button = wait.until(
        EC.element_to_be_clickable((By.ID, "btnSubmitContrat_accesRDC"))
    )
    submit_button.click()

    try:
        # Essaie de gérer la première modale avec le bouton nommé "OK"
        modal_button_ok = wait.until(EC.element_to_be_clickable((By.NAME, "OK")))
        modal_button_ok.click()
        print("Première modale gérée.")
    except TimeoutException:
        print("Pas de première modale à gérer.")

    try:
        # Essaie de gérer la deuxième modale avec le sélecteur CSS spécifique
        modal_button_selector = "body > div.bootbox.modal.fade.bootbox-alert.in > div > div > div.modal-footer > button"
        modal_button_css = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, modal_button_selector))
        )
        modal_button_css.click()
        print("Deuxième modale gérée.")
    except TimeoutException:
        print("Pas de deuxième modale à gérer.")
        # Attendre la visibilité de l'élément avec l'ID 'modalRefContrat'
        wait.until(EC.visibility_of_element_located((By.ID, "modalRefContrat")))


def save_non_modifiable_contract(contrat_number):
    """Enregistre le numéro de contrat dans un fichier JSON."""
    file_path = "Cas_4/non_modifiable_cas_4.json"
    try:
        # Lecture du fichier existant et ajout du nouveau contrat
        with open(file_path, "r+") as file:
            data = json.load(file)
            if contrat_number not in data:
                data.append(contrat_number)
                file.seek(0)
                json.dump(data, file)
    except FileNotFoundError:
        # Création d'un nouveau fichier si celui-ci n'existe pas
        with open(file_path, "w") as file:
            json.dump([contrat_number], file)


def switch_to_iframe_and_click_modification(driver, wait, contrat_number):
    print("Changement vers iframe et clic sur 'Modification'...")
    try:
        iframe_selector = "#modalRefContrat > div > div > div.modal-body > iframe"
        iframe = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, iframe_selector))
        )
        driver.switch_to.frame(iframe)
        print("switch to iframe")

        modification_button_selector = (
            "//permission/a[@href='#amendment']//div[@id='detailsModificationButton']"
        )
        bouton_modification = wait.until(
            EC.element_to_be_clickable((By.XPATH, modification_button_selector))
        )
        bouton_modification.click()
        print("Attente et validation des permissions accordées")
    except TimeoutException as e:
        # Enregistrement du numéro de contrat dans un fichier JSON si le bouton n'est pas trouvé
        print(
            f"Le bouton 'Modification' pour le contrat {contrat_number} n'est pas trouvé. Enregistrement dans le fichier non_modifiable.json"
        )
        save_non_modifiable_contract(contrat_number)
        raise  # Vous pouvez choisir de lever ou non une exception ici

    finally:
        driver.switch_to.default_content()


def wait_for_redirection(driver, wait):
    print("Attente de la redirection...")

    try:
        loader = (By.ID, "loader")
        WebDriverWait(driver, 8).until(EC.invisibility_of_element_located(loader))

        element = WebDriverWait(driver, 8).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "#content_offre > ul > li:nth-child(2) > a")
            )
        )
        element.click()

        print("Redirection réussie.")
    except TimeoutException as e:
        print(f"Erreur lors de l'interaction avec les éléments : {e}")
        driver.save_screenshot("debug_screenshot_erreur_redirection.png")
        raise
    except Exception as e:
        print(f"Erreur inattendue lors de la redirection : {e}")
        driver.save_screenshot("debug_screenshot_erreur_inattendue.png")

    try:
        # Obtenir le texte de l'en-tête h1 pour déterminer le type de contrat
        h1_text = driver.find_element(By.TAG_NAME, "h1").text

        # Vérifier le type de contrat et exécuter des actions en conséquence
        if "Affranchigo forfait" in h1_text:
            # Copier et coller les valeurs code Regate
            try:
                valeur_a_copier = driver.find_element(
                    By.CSS_SELECTOR, "[id='g0_p159|0_r486_c487[0]']"
                ).get_attribute("value")
                champ_cible = driver.find_element(
                    By.CSS_SELECTOR, "[id='g0_p159|0_r486_c487']"
                )
                champ_cible.clear()
                champ_cible.send_keys(valeur_a_copier)
                champ_cible.send_keys(Keys.TAB)
                # ... Autres opérations liées à cet élément
            except NoSuchElementException:
                print(
                    "La première partie du contrat est déjà traitée. Continuation avec les étapes suivantes."
                )
            # Attendre la mise à jour du Select et vérifier la présence d'options
            select_selector = "#g0_p159\\|0_r486\\[0\\] > div > critere-form:nth-child(3) > div.form-group.critere_psc > input-etb-prest > div > select"
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, select_selector))
            )
            select_element = Select(
                driver.find_element(By.CSS_SELECTOR, select_selector)
            )
            # Attendre que les options soient chargées dans le Select
            WebDriverWait(driver, 10).until(
                lambda driver: len(select_element.options) > 1
            )

           # Appuis sur Oui pour la fusion des rôles
            radio_button_selector = "#g0_p159\\|0_c25258_v1"
            try:
                radio_button = driver.find_element(
                    By.CSS_SELECTOR, radio_button_selector
                )
                radio_button.click()
            except ElementClickInterceptedException:
                print("Un autre élément bloque le clic sur le bouton radio.")
            except NoSuchElementException:
                print("Le bouton radio est introuvable.")


            some_element_selector = "g0_p159|0_r486_c3586_v3"

            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, some_element_selector)))
            except TimeoutException:
                print("Le temps d'attente pour la présence de l'élément spécifié est dépassé.")
            

            # Définis les deux sélecteurs CSS
            select_time_selectors = [
                "#g0_p159\\|0_r486\\[0\\] > div > critere-form:nth-child(7) > div.form-group.critere_psc > input-component > div.no-left-gutter.col-xs-8.col-sm-8.col-md-8 > select",
                "#g0_p159\\|0_r486\\[0\\] > div > critere-form:nth-child(5) > div.form-group.critere_psc > input-component > div.no-left-gutter.col-xs-8.col-sm-8.col-md-8 > select"
            ]

            found_selector = False

            for select_time_selector in select_time_selectors:
                try:
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, select_time_selector)))
                    WebDriverWait(driver, 10).until(lambda d: len(Select(d.find_element(By.CSS_SELECTOR, select_time_selector)).options) > 0)
                    select_time_element = Select(driver.find_element(By.CSS_SELECTOR, select_time_selector))
                    select_time_element.select_by_value("16H30")
                    found_selector = True
                    break  # Sélecteur trouvé et valeur sélectionnée, sortir de la boucle
                except (NoSuchElementException, TimeoutException, ElementNotInteractableException) as e:
                    print(f"Erreur avec le sélecteur : {select_time_selector}, Erreur : {e}")

            if not found_selector:
                print("Aucun sélecteur valide trouvé pour sélectionner l'heure.")


            # Trouver et cliquer sur le bouton de soumission
            try:
                    submit_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "form#odcFormCPV button[type='submit']"))
                    )
                    submit_button.click()

                    WebDriverWait(driver, 10).until(
                        EC.url_changes("https://www.deviscontrat.net-courrier.extra.laposte.fr/appli/ihm/configurateur/put-contract")
                    )
                    print("Formulaire soumis avec succès.")
                    print("Modification réussie.")
                
            except ElementClickInterceptedException:
                    print("Un autre élément bloque le clic sur le bouton de soumission.")
                    driver.save_screenshot("debug_screenshot_erreur_clic.png")
            except NoSuchElementException:
                    print("Le bouton de soumission est introuvable.")
                    driver.save_screenshot("debug_screenshot_erreur_bouton_introuvable.png")

        else:
            # Copier et coller les valeurs code Regate
            try:
                valeur_a_copier = driver.find_element(
                    By.ID, "g0_p265|0_r2055_c2056[0]"
                ).get_attribute("value")
                champ_cible = driver.find_element(By.ID, "g0_p265|0_r2055_c2056")
                champ_cible.clear()
                champ_cible.send_keys(valeur_a_copier)
                champ_cible.send_keys(Keys.TAB)
            except NoSuchElementException:
                print("La première partie du contrat est déjà traitée. Continuation avec les étapes suivantes.")

            # Attendre la mise à jour du Select et vérifier la présence d'options
            select_selector = "#g0_p265\\|0_r2055\\[0\\] > div > critere-form:nth-child(3) > div.form-group.critere_psc > input-etb-prest > div > select"
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, select_selector))
            )
            try:
                select_element = Select(
                    driver.find_element(By.CSS_SELECTOR, select_selector)
                )
                WebDriverWait(driver, 10).until(
                    lambda driver: len(select_element.options) > 1
                )
                try:
                    select_element.select_by_index(1)
                except NoSuchElementException:
                    print("L'option sélectionnée n'est pas disponible dans le select.")
                except ElementNotInteractableException:
                    print(
                        "Impossible d'interagir avec le select pour sélectionner une option."
                    )
            except TimeoutException:
                print("Temps d'attente dépassé pour la présence du select.")

            # Appuis sur Oui pour la fusion des rôles
            radio_button_selector = "#g0_p265\\|0_c24954_v1"
            try:
                radio_button = driver.find_element(
                    By.CSS_SELECTOR, radio_button_selector
                )
                radio_button.click()
            except ElementClickInterceptedException:
                print("Un autre élément bloque le clic sur le bouton radio.")
            except NoSuchElementException:
                print("Le bouton radio est introuvable.")

            # Remplacez 'some_element_selector' par le sélecteur de l'élément que vous attendez
            some_element_selector = "g0_p265|0_r2055_c3642_v3"
            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, some_element_selector)))
            except TimeoutException:
                print("Le temps d'attente pour la présence de l'élément spécifié est dépassé.")

            # Définis les deux sélecteurs CSS
            select_time_selectors = [
                "#g0_p265\\|0_r2055\\[0\\] > div > critere-form:nth-child(7) > div.form-group.critere_psc > input-component > div > select",
                "#g0_p265\\|0_r2055\\[0\\] > div > critere-form:nth-child(5) > div.form-group.critere_psc > input-component > div > select"
            ]

            found_selector = False

            for select_time_selector in select_time_selectors:
                try:
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, select_time_selector)))
                    WebDriverWait(driver, 10).until(lambda d: len(Select(d.find_element(By.CSS_SELECTOR, select_time_selector)).options) > 0)
                    select_time_element = Select(driver.find_element(By.CSS_SELECTOR, select_time_selector))
                    select_time_element.select_by_value("16H30")
                    found_selector = True
                    break  # Sélecteur trouvé et valeur sélectionnée, sortir de la boucle
                except (NoSuchElementException, TimeoutException, ElementNotInteractableException) as e:
                    print(f"Erreur avec le sélecteur : {select_time_selector}, Erreur : {e}")

            if not found_selector:
                print("Aucun sélecteur valide trouvé pour sélectionner l'heure.")


        # Trouver et cliquer sur le bouton de soumission
            try:
                submit_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, "form#odcFormCPV button[type='submit']")
                    )
                )
                submit_button.click()

                WebDriverWait(driver, 10).until(
                    EC.url_changes(
                        url_redirection
                    )
                )
                print("Formulaire soumis avec succès.")
                print("Modification réussie.")

            except ElementClickInterceptedException:
                print("Un autre élément bloque le clic sur le bouton de soumission.")
                driver.save_screenshot("debug_screenshot_erreur_clic.png")
            except NoSuchElementException:
                print("Le bouton de soumission est introuvable.")
                driver.save_screenshot("debug_screenshot_erreur_bouton_introuvable.png")

    except NoSuchElementException as e:
        print(f"Erreur : Élément non trouvé. {e}")
        driver.save_screenshot("debug_screenshot_erreur_element.png")
    except Exception as e:
        print(f"Erreur inattendue : {e}")
        driver.save_screenshot("debug_screenshot_erreur_inattendue.png")


def process_contract(driver, wait, numero_contrat):
    try:
        print(f"Traitement du contrat numéro {numero_contrat}...")

        # Soumettre le numéro de contrat
        submit_contract_number(driver, wait, numero_contrat)

        # Changer vers iframe et cliquer sur 'Modification'
        switch_to_iframe_and_click_modification(driver, wait, numero_contrat)

        # Attendre la redirection et effectuer des actions supplémentaires
        wait_for_redirection(driver, wait)

        print(f"Traitement du contrat numéro {numero_contrat} terminé.")
    except Exception as e:
        print(f"Erreur lors du traitement du contrat {numero_contrat}: {e}")
        # Gérer l'exception ou effectuer une récupération ici

    # Retour à l'URL de départ
    url_de_depart = "https://www.deviscontrat.net-courrier.extra.laposte.fr/appli/ihm/index/acces-dc"
    driver.get(url_de_depart)


def main():
    print("Démarrage du script...")
    driver, wait = configure_selenium()
    login(driver, wait)

    numeros_contrat = process_json_files(driver, wait)
    for numero_contrat in numeros_contrat:
        if numero_contrat:
            process_contract(driver, wait, numero_contrat)
        else:
            print("Aucun numéro de contrat trouvé.")

    driver.save_screenshot("debug_screenshot_avant_fermeture.png")
    driver.quit()
    print("Fermeture du navigateur.")


if __name__ == "__main__":
    main()
