import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os


def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(
        ChromeDriverManager().install()), options=options)
    return driver


def safe_click(driver, by, locator, timeout=5, retries=2, stop_if_fails=True):
    for attempt in range(retries):
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((by, locator))
            )
            element.click()
            return
        except:
            print(f"Attempt {attempt + 1} to click {locator} failed: {e}")
            time.sleep(0.5)
    if stop_if_fails:
        raise Exception(
            f"Failed to click on element after {retries} attempts: {locator}")


def safe_select_dropdown_option(driver, by, locator, option_text, timeout=5, retries=2):
    for attempt in range(retries):
        try:
            dropdown = WebDriverWait(driver, timeout).until(
                EC.visibility_of_element_located((by, locator))
            )
            select = Select(dropdown)
            if select.first_selected_option.text == option_text:
                return
            select.select_by_visible_text(option_text)
            return
        except:
            time.sleep(0.5)
    raise Exception(
        f"Failed to select option '{option_text}' after {retries} attempts: {locator}")


def save_page(driver, filename):
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(soup.prettify())


def get_program_options(driver, by, locator, timeout=20):
    try:
        dropdown = WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((by, locator))
        )
        select = Select(dropdown)
        program_options = [
            option.text for option in select.options if option.text.strip() != "-"
        ]
        return program_options
    except TimeoutException:
        return []


def get_catalog_year(driver):
    try:
        catalog_year_dropdown = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "catalogYearTerm"))
        )
        select = Select(catalog_year_dropdown)
        options = [
            option.text for option in select.options if option.text.strip() != "-"]

        fall_options = [opt for opt in options if opt.startswith("Fall")]
        spring_options = [opt for opt in options if opt.startswith("Spring")]

        if fall_options:
            return fall_options[0]
        elif spring_options:
            return spring_options[0]
        else:
            return None
    except TimeoutException:
        return None


def get_track_options(driver, timeout=5):
    try:
        add_child_button = WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((By.ID, "addChild"))
        )

        if add_child_button.get_attribute("value") not in ["Track", "Concentration"]:
            print("No valid Track or Concentration options available.")
            return []

        safe_click(driver, By.ID, "addChild", timeout=timeout)

        dropdown = WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located(
                (By.ID, "newMarker.replacementValue"))
        )
        select = Select(dropdown)
        track_options = [
            option.text for option in select.options if option.text.strip() != "-"
        ]

        return track_options
    except (TimeoutException, NoSuchElementException) as e:
        print(f"Error fetching track/concentration options: {e}")
        return []


def collect_programs(driver):
    program_catalog_list = []
    try:
        driver.get("https://uac-bos-prd.umasscs.net/selfservice/")

        safe_click(driver, By.CSS_SELECTOR, "#selectedProgramHeading a")

        WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.ID, "whatIfDegreeProgram"))
        )

        program_options = get_program_options(
            driver, By.ID, "whatIfDegreeProgram", timeout=15)

        for program_name in program_options:
            print(f"Adding program: {program_name}")
            try:
                try:
                    safe_click(driver, By.ID, "changeProgramButton",
                               stop_if_fails=False)
                except Exception:
                    pass

                # Select the program
                safe_select_dropdown_option(
                    driver, By.ID, "whatIfDegreeProgram", program_name, timeout=5, retries=2)

                # Get and select the catalog year
                catalog_year = get_catalog_year(driver)
                if catalog_year:
                    safe_select_dropdown_option(
                        driver, By.ID, "catalogYearTerm", catalog_year)
                    print(f"Selected Catalog Year: {catalog_year}")
                else:
                    print(
                        f"No catalog year available for program: {program_name}. Skipping.")
                    continue

                program_catalog_list.append((program_name, catalog_year, None))

                # Get track or concentration options
                track_options = get_track_options(driver)
                if track_options:
                    for track_name in track_options:
                        print(
                            f"Adding program with track/concentration: {program_name} - {track_name}")
                        program_catalog_list.append(
                            (program_name, catalog_year, track_name))

            except Exception as e:
                print(f"Error adding program '{program_name}': {e}")

        try:
            safe_click(driver, By.ID, "changeProgramButton",
                       stop_if_fails=False)
            safe_select_dropdown_option(
                driver, By.ID, "whatIfDegreeProgram", "-", timeout=5, retries=2)
        except:
            pass

        return program_catalog_list

    except Exception as e:
        print(
            f"An error occurred while collecting program-catalog-track tuples: {e}")
        return program_catalog_list


def process_program(driver, program_name, catalog_year, track_name):
    try:
        driver.get("https://uac-bos-prd.umasscs.net/selfservice/")

        safe_click(driver, By.CSS_SELECTOR, "#selectedProgramHeading a")

        # Reset selections
        try:
            safe_click(driver, By.ID, "changeProgramButton",
                       stop_if_fails=False)
        except Exception:
            pass

        WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.ID, "whatIfDegreeProgram"))
        )

        # Select the program
        safe_select_dropdown_option(
            driver, By.ID, "whatIfDegreeProgram", program_name)

        # Select the catalog year
        safe_select_dropdown_option(
            driver, By.ID, "catalogYearTerm", catalog_year)

        # If there's a track/concentration, select it
        if track_name:
            safe_click(driver, By.ID, "addChild")

            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located(
                    (By.ID, "newMarker.replacementValue"))
            )
            safe_select_dropdown_option(
                driver, By.ID, "newMarker.replacementValue", track_name)

        # Make audit
        safe_click(driver, By.LINK_TEXT, "Click to view available options.")

        safe_select_dropdown_option(
            driver, By.ID, "reportType", "Regular (HTML)")

        safe_click(driver, By.ID, "runAudit")

        WebDriverWait(driver, 25).until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[@id='auditSummary']/tbody/tr[1]/td[2]/div/div[1]/span"))
        )

        safe_program_name = "".join(
            c for c in program_name if c.isalnum() or c in (" ", "_", "-")).rstrip()
        if track_name:
            safe_track_name = "".join(
                c for c in track_name if c.isalnum() or c in (" ", "_", "-")).rstrip()
            filename = f"data/programs/{safe_program_name}/{safe_program_name}-{safe_track_name}.html"
        else:
            filename = f"data/programs/{safe_program_name}/{safe_program_name}.html"

        save_page(driver, filename)
        print(
            f"Saved page for program '{program_name}', catalog year '{catalog_year}', track '{track_name}' to '{filename}'.")

    except Exception as e:
        print(
            f"Error processing program '{program_name}', catalog year '{catalog_year}', track '{track_name}': {e}")


def main():
    driver = init_driver()

    try:
        driver.get("https://www.umb.edu/it/software-systems/wiser/")
        input("Press enter once logged in")

        # Collect (program_name, catalog_year, track_name) tuples
        program_catalog_tuples = collect_programs(driver)
        print(
            f"Collected {len(program_catalog_tuples)} program-catalog-track tuples.")

        # Process each tuple
        for program_name, catalog_year, track_name in program_catalog_tuples:
            process_program(driver, program_name,
                            catalog_year, track_name)

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
