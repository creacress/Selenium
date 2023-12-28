import os
import json
import time
import threading
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementNotInteractableException,
    ElementClickInterceptedException,
    WebDriverException,
)
from affranchigo_forfait_case import AffranchigoForfaitCase

from affranchigo_lib_case import AffranchigoFLibCase

from debug import log_error_and_capture_screenshot, setup_logger


# Initatilisation du debug
logger = setup_logger
# Charge les variables d'env si nécessaire
load_dotenv()

# Accéder aux variables
identifiant = os.getenv("IDENTIFIANT")
mot_de_passe = os.getenv("MOT_DE_PASSE")


def configure_selenium():
    print("Configuration de Selenium...")
    service = Service("data/msedgedriver.exe")
    driver = webdriver.Edge(service=service)
    driver.get(
        "https://www.deviscontrat.net-courrier.extra.laposte.fr/appli/ihm/index/acces-dc?profil=ADV"
    )
    wait = WebDriverWait(driver, 3)
    return driver, wait


def check_and_handle_modal(driver):
    while True:
        try:
            # Essaie de gérer la première modale avec le bouton nommé "OK"
            modal_button_ok = driver.find_element(
                By.NAME,
                  "OK"
                )
            if modal_button_ok.is_displayed():
                modal_button_ok.click()
                print("Première modale gérée.")

             # Vérifier et gérer la Deuxième Modale   
            modal_button_css = driver.find_element(
                By.CSS_SELECTOR,
                "body > div.bootbox.modal.fade.bootbox-alert.in > div > div > div.modal-footer > button"
                )
            if modal_button_css.is_displayed():
                modal_button_css.click()
                print("Deuxième Modale gérée")
            
            # Vérifier et gérer la Modale Permission
            modal_button_1 = driver.find_element(
                By.CSS_SELECTOR,
                "body > div.swal2-container.swal2-center.swal2-fade.swal2-shown > div > div.swal2-buttonswrapper > button.swal2-confirm.swal2-styled",
            )
            if modal_button_1.is_displayed():
                modal_button_1.click()
                driver.refresh()
                print("Modale permission gérée.")

            # Vérifier et gérer la Modale API erreur
            modal_button_2 = driver.find_element(
                By.CSS_SELECTOR,
                "body > div.swal2-container.swal2-center.swal2-backdrop-show > div > div.swal2-actions > button.swal2-confirm.swal2-styled",
            )
            if modal_button_2.is_displayed():
                modal_button_2.click()
                driver.refresh()
                print("Modale API erreur gérée.")
        except NoSuchElementException:
            # Les modales ne sont pas présentes
            pass

        time.sleep(1)  # Vérifie toutes les secondes


def login(driver, wait):
    print("Tentative de connexion...")

    try:
        input_identifiant = wait.until(
            EC.presence_of_element_located((By.ID, "AUTHENTICATION.LOGIN"))
        )
        input_identifiant.clear()
        input_identifiant.send_keys(identifiant)
        input_identifiant.send_keys(Keys.RETURN)

        input_mot_de_passe = wait.until(
            EC.presence_of_element_located((By.ID, "AUTHENTICATION.PASSWORD"))
        )
        input_mot_de_passe.clear()
        input_mot_de_passe.send_keys(mot_de_passe)
        input_mot_de_passe.send_keys(Keys.RETURN)
    except TimeoutException:
        print("Déjà connecté ou le champ d'identifiant n'est pas présent.")
    except Exception as e:
        log_error_and_capture_screenshot(driver, "Problème Login", e)


def process_json_files(file_path):
    print("Traitement du fichier JSON pour les contrats...")
    numeros_contrat = []

    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            data = json.load(file)
            numeros_contrat = list(data.values())

    return numeros_contrat


def submit_contract_number(driver, wait, numero):
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
        # Attendre la visibilité de l'élément avec l'ID 'modalRefContrat'
        wait.until(EC.visibility_of_element_located((By.ID, "modalRefContrat")))
    except:
        print('Modale Ref Contrat problème')

def save_processed_contracts(contrats):
    """Enregistre les numéros de contrats traités dans un fichier JSON."""
    file_path = "numeros_contrat_traites_cas_3.json"
    try:
        # Lecture du fichier existant et ajout des nouveaux contrats
        with open(file_path, "r+") as file:
            existing_data = json.load(file)
            updated_data = existing_data + [
                c for c in contrats if c not in existing_data
            ]
            file.seek(0)
            json.dump(updated_data, file)
    except FileNotFoundError:
        # Création d'un nouveau fichier si celui-ci n'existe pas
        with open(file_path, "w") as file:
            json.dump(contrats, file)


def save_non_modifiable_contract(contrat_number):
    """Enregistre le numéro de contrat dans un fichier JSON."""
    file_path = "non_modifiable_cas_3.json"
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

        modification_button_selector = (
            "//permission/a[@href='#amendment']//div[@id='detailsModificationButton']"
        )
        bouton_modification = wait.until(
            EC.element_to_be_clickable((By.XPATH, modification_button_selector))
        )
        bouton_modification.click()

    except TimeoutException as e:
        # Enregistrement du numéro de contrat dans un fichier JSON si le bouton n'est pas trouvé
        print(
            f"Le bouton 'Modification' pour le contrat {contrat_number} n'est pas trouvé. Enregistrement dans le fichier non_modifiable.json"
        )
        save_non_modifiable_contract(contrat_number)
        url_de_depart = "https://www.deviscontrat.net-courrier.extra.laposte.fr/appli/ihm/index/acces-dc"
        driver.get(url_de_depart)
        raise  # Vous pouvez choisir de lever ou non une exception ici

    finally:
        driver.switch_to.default_content()


def wait_for_redirection(driver, wait):
    print("Attente de la redirection...")

    try:
        loader = (By.ID, "loader")
        WebDriverWait(driver, 10).until(EC.invisibility_of_element_located(loader))

        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "#content_offre > ul > li:nth-child(2) > a")
            )
        )
        element.click()

        print("Redirection réussie.")
    except TimeoutException as e:
        print(f"Erreur lors de l'interaction avec les éléments : {e}")
        log_error_and_capture_screenshot(driver, "Erreur_Redirection_temps", e)
        raise
    except Exception as e:
        print(f"Erreur inattendue lors de la redirection : {e}")
        driver.save_screenshot("debug_screenshot_erreur_inattendue.png")
        log_error_and_capture_screenshot(driver, "Erreur_Redirection_autre", e)


def modification_condition_ventes(driver, wait):
    # Permet de vérifier quel cas ont va gérer
    # Cas Forfait
    forfait_select_1_selector = "#g0_p159\\|0_r486\\[0\\] > div > critere-form:nth-child(3) > div.form-group.critere_psc > input-etb-prest > div > select"
    forfait_select_2_selector = "#\\[g0_p159\\|0_r486\\[0\\]\\] > div > critere-form:nth-child(3) > div.form-group.critere_psc > input-etb-prest > div > select"
    # Cas Liberté
    liberte_select_1_selector = "#g0_p265\\|0_r2055\\[0\\] > div > critere-form:nth-child(3) > div.form-group.critere_psc > input-etb-prest > div > select"
    liberte_select_2_selector = "#\\[g0_p265\\|0_r2055\\[0\\]\\] > div > critere-form:nth-child(3) > div.form-group.critere_psc > input-etb-prest > div > select"
    # Création d'une instance de la classe AffranchigoForfaitCase
    affranchigo_forfait_case = AffranchigoForfaitCase(driver)
    # Création de l'instance de la classe AffranchigoFLibCase
    affranchigo_liberte_case = AffranchigoFLibCase(driver)

    try:
        h1_text = driver.find_element(By.TAG_NAME, "h1").text
        print(f"Texte de l'en-tête H1: {h1_text}")
        if "Affranchigo forfait" in h1_text:
            try:
                select_element = driver.find_element(
                    By.CSS_SELECTOR,
                    "#cptLeft > div:nth-child(7) > critere-form > div.form-group.critere_offre > input-itl-ope > input-component > div > select",
                )
                select_interlocuteur = Select(select_element)
                if len(select_interlocuteur.options) > 1:
                    select_interlocuteur.select_by_index(1)
                    print("Sélecteur interlocuteur opérationnel sélectionné.")
                else:
                    print(
                        "Le sélecteur interlocuteur opérationnel ne contient pas d'options sélectionnables."
                    )
            except NoSuchElementException:
                print("L'élément select interlocuteur opérationnel n'a pas été trouvé.")
            except Exception as e:
                print(
                    f"Erreur inattendue avec le sélecteur interlocuteur opérationnel : {e}"
                )
                log_error_and_capture_screenshot(
                    driver, "Selecteur_interlocuteur_non_trouvé", e
                )

            try:
                # Initialise les variables pour vérifier la présence des sélecteurs
                forfait_select_1_found = False
                forfait_select_2_found = False
                forfait_select_1_options = 0
                forfait_select_2_options = 0

                # Vérifier le selecteur 1
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, forfait_select_1_selector)
                        )
                    )
                    select_1 = Select(
                        driver.find_element(By.CSS_SELECTOR, forfait_select_1_selector)
                    )
                    forfait_select_1_options = len(select_1.options)
                    forfait_select_1_found = True
                except (NoSuchElementException, TimeoutException):
                    print("Selecteur 1 non trouvé ou non visible")

                # Vérifier le selecteur 2
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, forfait_select_2_selector)
                        )
                    )
                    select_2 = Select(
                        driver.find_element(By.CSS_SELECTOR, forfait_select_2_selector)
                    )
                    forfait_select_2_options = len(select_2.options)
                    forfait_select_2_found = True
                except (NoSuchElementException, TimeoutException):
                    print("Selecteur 2 non trouvé ou non visible")

                    # Logique pour décider quel cas utiliser
                if (
                    forfait_select_1_found
                    and forfait_select_1_options > 1
                    and not forfait_select_2_found
                ):
                    print(
                        "Utilisation du cas 3 (select_1 est présent avec options et select_2 est absent)"
                    )
                    affranchigo_forfait_case.handle_case_3(driver)

                elif (
                    forfait_select_2_found
                    and forfait_select_2_options > 1
                    and not forfait_select_1_found
                ):
                    print(
                        "Utilisation du cas 3 (select_2 est présent avec options et select_1 est absent)"
                    )
                    affranchigo_forfait_case.handle_case_3(driver)

                elif (
                    forfait_select_1_found
                    and forfait_select_2_found
                    and (forfait_select_1_options <= 1 or forfait_select_2_options <= 1)
                ):
                    print(
                        "Utilisation du cas 2 (les deux sélecteurs sont présents mais au moins l'un est vide)"
                    )
                    affranchigo_forfait_case.handle_case_2(driver)

                elif (
                    forfait_select_1_found
                    and forfait_select_2_found
                    and (forfait_select_1_options > 1 and forfait_select_2_options > 1)
                ):
                    print(
                        "Utilisation du cas 2 (les deux sélecteurs sont présents et avec options)"
                    )
                    affranchigo_forfait_case.handle_case_2(driver)

                elif not forfait_select_1_found and not forfait_select_2_found:
                    print("Aucun des sélecteurs n'est présent")
                # Gérer le cas où aucun sélecteur n'est trouvé
                else:
                    print("Aucun cas applicable ou logique de décision à revoir.")
            except Exception as e:
                print(f"Erreur inattendue : {e}")
                log_error_and_capture_screenshot(
                    driver,
                    "Aucun cas Forfait applicable ou logique de décision à revoir",
                    e,
                )

            # Clique sur "Conditions Particulières de Réalisations"
            try:
                bouton_haut = driver.find_element(
                    By.CSS_SELECTOR,
                    "body > app-root > offre-form > app-odc-header > aside > div.user_infos > a",
                )
                driver.execute_script("arguments[0].scrollIntoView();", bouton_haut)
                element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, "#content_offre > ul > li:nth-child(3) > a")
                    )
                )
                element.click()
                print("Le clique à bien été effectué")
            except (TimeoutException, NoSuchElementException, Exception) as e:
                log_error_and_capture_screenshot(
                    driver,
                    "Onglet Conditions Particulières de ventes non trouvé ou cliquable",
                    e,
                )

            try:
                # Trouve l'élément et crée une instance de Select
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (
                            By.CSS_SELECTOR,
                            "#p159CPR > critere-form > div.form-group.critere_psc > input-component > div > select",
                        )
                    )
                )
                select_heures_depot = Select(element)

                # Vérifie la valeur sélectionnée actuelle
                current_value = select_heures_depot.first_selected_option.get_attribute(
                    "value"
                )
                if current_value in ["", "null"]:
                    select_heures_depot.select_by_index(3)
                    print("Une nouvelle heure a été sélectionnée.")
                else:
                    print(
                        "Une heure est déjà sélectionnée, aucune action supplémentaire n'est requise."
                    )
            except Exception as e:
                print(
                    f"Erreur lors de la manipulation du select pour les heures de dépôt : {e}"
                )

            # Trouver et cliquer sur le bouton de soumission
            try:
                submit_button = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located(
                        (By.CSS_SELECTOR, "#odcFormCPR > button")
                    )
                )
                submit_button.click()

                WebDriverWait(driver, 10).until(
                    EC.url_changes(
                        "https://www.deviscontrat.net-courrier.extra.laposte.fr/appli/ihm/configurateur/put-contract"
                    )
                )
                print("Formulaire soumis avec succès.")
                time.sleep(1)
                try:
                    # Retour à l'URL de départ
                    url_de_depart = "https://www.deviscontrat.net-courrier.extra.laposte.fr/appli/ihm/index/acces-dc"
                    driver.get(url_de_depart)
                    print("Retour à l'URL de départ réussi.")
                except Exception as e:
                    print(f"Erreur lors de la navigation vers l'URL de départ : {e}")
                    driver.save_screenshot("debug_screenshot_erreur_retour.png")

            except TimeoutException:
                print("Le bouton de soumission n'as pas été trouvé dans les temps")
                driver.save_screenshot("debug_screenshot_erreur_clic.png")
            except Exception as e:
                print(f"Erreur lors de la soumission formulaire : {e}")
                driver.save_screenshot("debug_screenshot_erreur_soumission.png")

        else:
            print("Affranchigo Liberté")
            try:
                # Initialise les variables pour vérifier la présence des sélecteurs
                liberte_select_1_found = False
                liberte_select_2_found = False
                liberte_select_1_options = 0
                liberte_select_2_options = 0

                # Vérifier le selecteur 1
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, liberte_select_1_selector)
                        )
                    )
                    select_1 = Select(
                        driver.find_element(By.CSS_SELECTOR, liberte_select_1_selector)
                    )
                    liberte_select_1_options = len(select_1.options)
                    liberte_select_1_found = True
                except (NoSuchElementException, TimeoutException):
                    print("Selecteur 1 non trouvé ou non visible")

                # Vérifier le selecteur 2
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, liberte_select_2_selector)
                        )
                    )
                    select_2 = Select(
                        driver.find_element(By.CSS_SELECTOR, liberte_select_2_selector)
                    )
                    liberte_select_2_options = len(select_2.options)
                    liberte_select_2_found = True
                except (NoSuchElementException, TimeoutException):
                    print("Selecteur 2 non trouvé ou non visible")

                    # Logique pour décider quel cas utiliser
                if (
                    liberte_select_1_found
                    and liberte_select_1_options > 1
                    and not liberte_select_2_found
                ):
                    print(
                        "Utilisation du cas 1 (select_1 est présent avec options et select_2 est absent)"
                    )
                    affranchigo_liberte_case.handle_liberte_case_1(driver)

                elif (
                    liberte_select_2_found
                    and liberte_select_2_options > 1
                    and not liberte_select_1_found
                ):
                    print(
                        "Utilisation du cas 1 (select_2 est présent avec options et select_1 est absent)"
                    )
                    affranchigo_liberte_case.handle_liberte_case_1(driver)

                elif (
                    liberte_select_1_found
                    and liberte_select_2_found
                    and (liberte_select_1_options <= 1 or liberte_select_2_options <= 1)
                ):
                    print(
                        "Utilisation du cas 3 (les deux sélecteurs sont présents mais au moins l'un est vide)"
                    )
                    affranchigo_liberte_case.handle_liberte_case_3(driver)

                elif (
                    liberte_select_1_found
                    and liberte_select_2_found
                    and (liberte_select_1_options > 1 and liberte_select_2_options > 1)
                ):
                    print(
                        "Utilisation du cas 3 (les deux sélecteurs sont présents et avec options)"
                    )
                    affranchigo_liberte_case.handle_liberte_case_3(driver)

                elif not liberte_select_1_found and not liberte_select_2_found:
                    print("Aucun des sélecteurs n'est présent")
                # Gérer le cas où aucun sélecteur n'est trouvé
                else:
                    print("Aucun cas applicable ou logique de décision à revoir.")
            except Exception as e:
                print(f"Erreur inattendue : {e}")
                log_error_and_capture_screenshot(
                    driver,
                    "Aucun cas Liberté applicable ou logique de décision à revoir ",
                    e,
                )

            # Trouver et cliquer sur le bouton de soumission
            try:
                submit_button = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located(
                        (By.CSS_SELECTOR, "#odcFormCPV > button")
                    )
                )
                submit_button.click()

                WebDriverWait(driver, 10).until(
                    EC.url_changes(
                        "https://www.deviscontrat.net-courrier.extra.laposte.fr/appli/ihm/configurateur/put-contract"
                    )
                )
                print("Formulaire soumis avec succès.")
                time.sleep(1)
                try:
                    # Retour à l'URL de départ
                    url_de_depart = "https://www.deviscontrat.net-courrier.extra.laposte.fr/appli/ihm/index/acces-dc"
                    driver.get(url_de_depart)
                    print("Retour à l'URL de départ réussi.")
                except Exception as e:
                    print(f"Erreur lors de la navigation vers l'URL de départ : {e}")
                    driver.save_screenshot("debug_screenshot_erreur_retour.png")

            except TimeoutException:
                print("Le bouton de soumission n'as pas été trouvé dans les temps")
                driver.save_screenshot("debug_screenshot_erreur_clic.png")
            except Exception as e:
                print(f"Erreur lors de la soumission formulaire : {e}")
                driver.save_screenshot("debug_screenshot_erreur_soumission.png")

    except NoSuchElementException as e:
        print(f"Erreur : Élément non trouvé. {e}")
        driver.save_screenshot("debug_screenshot_erreur_element.png")
    except Exception as e:
        print(f"Erreur inattendue : {e}")
        driver.save_screenshot("debug_screenshot_erreur_inattendue.png")
        log_error_and_capture_screenshot(driver, "Erreur innatendue", e)


def process_contract(driver, wait, numero_contrat):
    try:
        print(f"Traitement du contrat numéro {numero_contrat}...")

        # Soumettre le numéro de contrat
        submit_contract_number(driver, wait, numero_contrat)

        # Changer vers iframe et cliquer sur 'Modification'
        switch_to_iframe_and_click_modification(driver, wait, numero_contrat)

        # Attendre la redirection et effectuer des actions supplémentaires
        wait_for_redirection(driver, wait)

        # Modifications "Conditions Particulières de Ventes"
        modification_condition_ventes(driver, wait)

        print(f"Traitement du contrat numéro {numero_contrat} terminé.")
        # Enregistrement du temps par contrat
    except Exception as e:
        print(f"Erreur lors du traitement du contrat {numero_contrat}: {e}")
        log_error_and_capture_screenshot(
            driver, f"Erreur lors du traitement du contrat {numero_contrat}", e
        )


def main():
    print("Démarrage du script...")
    driver, wait = configure_selenium()
    login(driver, wait)

    file_path = "data/cas_3.json"
    numeros_contrat = process_json_files(file_path)

    # Création et démarrage du thread
    modal_thread = threading.Thread(target=check_and_handle_modal, args=(driver,))
    modal_thread.daemon = True
    modal_thread.start()

    # Initialiser un compteur pour suivre le nombre de contrats traités
    compteur = 0

    for numero_contrat in numeros_contrat:
        if compteur >= 200:
            print("Limite de 200 contrats atteinte.")
            break  # Arrêter la boucle si 200 contrats ont été traités

        if numero_contrat:
            print(f"Traitement du contrat numéro {numero_contrat}...")
            process_contract(driver, wait, numero_contrat)
            compteur += 1
            print(f"Nombre de contrats traités : {compteur}")

            # Enregistrement du contrat traité
            save_processed_contracts([numero_contrat])

    driver.save_screenshot("debug_screenshot_avant_fermeture.png")
    driver.quit()
    print("Fermeture du navigateur.")


if __name__ == "__main__":
    main()
