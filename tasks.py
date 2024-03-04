from robocorp.tasks import task
from robocorp import workitems, vault
from RPA.Browser.Selenium import Selenium

import time
import re
from bs4 import BeautifulSoup

browser_lib = Selenium()



def open_the_website(url):
    print(f'Opening website: {url}')
    browser_lib.open_available_browser(url)



@task
def renew_loans(book_names : list):
    """"""

    input_id = "primary_comment"
    link = "https://piki.finna.fi/myresearch/userlogin"

    piki_credentials = vault.get_secret("piki_card_number")
    piki_card_number = piki_credentials['card']
    piki_pin = piki_credentials['pin']


    # Opening the invoice page link
    browser_lib.open_available_browser(link)

    card_input_id = "id:login_MultiILS_username"

    pin_input_id = "id:login_MultiILS_password"

    # Wait for the element to be visible (optional, but recommended to ensure the page has loaded)
    browser_lib.wait_until_element_is_visible(card_input_id, timeout=30)

    # Insert text into the card number field
    browser_lib.input_text(card_input_id, piki_card_number)

    # Insert text into the pincode field
    browser_lib.input_text(pin_input_id, piki_pin)

    # Click the button by its value
    browser_lib.click_element("xpath=//input[@type='submit' and @value='Kirjaudu']")

    # Loans page

    time.sleep(1)

    # Renew loans for each book
    for book_name in book_names:

        # Define the XPath for the title element containing the specific text
        xpath_for_title = f"//a[contains(@class, 'record-title') and contains(text(), '{book_name}')]"
        xpath_for_checkbox = f"{xpath_for_title}/ancestor::tr//input[@type='checkbox']"

        # Wait for the checkbox to be present
        browser_lib.wait_until_element_is_visible(xpath_for_checkbox, timeout=30)

        # Click the checkbox
        browser_lib.click_element(xpath_for_checkbox)

    # Wait for the button to be visible and interactable
    browser_lib.wait_until_element_is_visible("id:renewSelected", timeout=30)

    # Then click the button
    browser_lib.click_element("id:renewSelected")

    # Confirm the choice
    browser_lib.wait_until_element_is_visible("id:confirm_renew_selected_yes", timeout=30)

    # Then click the button
    browser_lib.click_element("id:confirm_renew_selected_yes")

    # Sleep for 5 seconds
    time.sleep(5)

    print(f"This task has been completed successfully")






@task
def process_emails_and_scrape_book_numbers():
    """Read email and scrape data"""

    print(f"Starting processing")


    for item in workitems.inputs:
        try:
            # We'll use HTML parsing to extract the link from the email, because reforwarded email standard content is empty
            email = item.email()
            email_html = email.html

            # Parse the HTML content
            soup = BeautifulSoup(email_html, 'html.parser')
        except Exception as e:
            print(f"Error processing email and scraping invoices: {e}")

    # Convert the soup object to text and search for the barcode pattern
    email_text = soup.get_text()

    # Adjust the pattern as necessary based on the expected format of the barcode
    #barcode_pattern = r"Barcode: (\w+)"
    title_pattern = r"Title: (.*?)Due date"

    # Use re.findall to get all occurrences of the barcode pattern in the email content
    titles = re.findall(title_pattern, email_text, re.DOTALL)

    renew_loans(titles)

    # barcodes will be a list of all matched barcode values
    print("Titles: ", titles)

    # Use the variables as needed
    print(f"Email content: {email_text}")




# Run the task
if __name__ == "__main__":
    process_emails_and_scrape_book_numbers()



