import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# Initialize the webdriver
driver = webdriver.Chrome(executable_path='/path/to/chromedriver')

def login_amazon(username, password):
    # Open Amazon login page
    driver.get("https://www.amazon.in/ap/signin")
    
    # Fill in login details
    driver.find_element(By.ID, 'ap_email').send_keys(username)
    driver.find_element(By.ID, 'continue').click()
    driver.find_element(By.ID, 'ap_password').send_keys(password)
    driver.find_element(By.ID, 'signInSubmit').click()

def scrape_bestsellers(category_url):
    driver.get(category_url)
    time.sleep(3)  # Wait for the page to load

    products = []
    try:
        while True:
            # Wait for products to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".zg-item-immersion"))
            )

            # Extract product information
            product_elements = driver.find_elements(By.CSS_SELECTOR, '.zg-item-immersion')
            for product in product_elements:
                try:
                    name = product.find_element(By.CSS_SELECTOR, '.p13n-sc-truncate').text
                    price = product.find_element(By.CSS_SELECTOR, '.p13n-sc-price').text
                    rating = product.find_element(By.CSS_SELECTOR, '.a-icon-alt').text
                    discount = product.find_element(By.CSS_SELECTOR, '.p13n-sc-price-discount').text
                    
                    # Ensure discount > 50%
                    if discount:
                        discount_percentage = int(discount.strip('%'))
                        if discount_percentage <= 50:
                            continue

                    # Store product data
                    products.append({
                        'name': name,
                        'price': price,
                        'rating': rating,
                        'discount': discount,
                        'category': category_url
                    })
                except Exception as e:
                    print(f"Error extracting product: {e}")
            
            # Try to go to the next page
            next_button = driver.find_element(By.CSS_SELECTOR, '.zg_pagination a.zg_page')
            if next_button:
                next_button.click()
                time.sleep(3)
            else:
                break  # End loop if no more pages

    except Exception as e:
        print(f"Error in scraping: {e}")
    
    return products

def main():
    # Log into Amazon
    username = "your_amazon_username"
    password = "your_amazon_password"
    login_amazon(username, password)

    categories = [
        "https://www.amazon.in/gp/bestsellers/kitchen/ref=zg_bs_nav_kitchen_0",
        "https://www.amazon.in/gp/bestsellers/shoes/ref=zg_bs_nav_shoes_0",
        "https://www.amazon.in/gp/bestsellers/computers/ref=zg_bs_nav_computers_0",
        "https://www.amazon.in/gp/bestsellers/electronics/ref=zg_bs_nav_electronics_0"
        # Add 6 more categories as needed
    ]

    all_products = []
    for category_url in categories:
        products = scrape_bestsellers(category_url)
        all_products.extend(products)
    
    # Store the data in CSV format
    df = pd.DataFrame(all_products)
    df.to_csv('amazon_bestsellers.csv', index=False)

if __name__ == "__main__":
    main()
