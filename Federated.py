import argparse
from FederatedPreparer import FederatedPreparer
from Evaluate import Test
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Federated:
    
    def __init__(self,args):
        self.num_users = args.nb_users
        self.batch_size = args.batch_size
        self.mode = args.mode
        self.communication_round = args.nb_roc
        self.learning_rate = args.lr
        self.federated_preparer = FederatedPreparer(self.num_users,self.batch_size)
        self.url = 'http://localhost:8080'
        
        
    def launch_federated_headless(self,url):
        
        options = Options()
        options.add_argument('--headless')  # Run in headless mode for no UI
        service = Service('/usr/local/bin/geckodriver')  # Update this path to your WebDriver
        driver = webdriver.Firefox(service=service, options=options)
        
        try:
            # Open the web application
            driver.get(url)
            
            # Wait until the page is loaded and a specific element is present (modify the selector as needed)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))  # You can change this to a more specific element
            )
            
            # Check if the page contains expected content (modify this as needed)
            page_title = driver.title
            if page_title:
                print(f"Success: Connected to the web app. Page title is '{page_title}'.")
            else:
                print("Error: Unable to retrieve the page title.")
                
            button = driver.find_element(By.ID, 'launch_federated')
            
            if button:
                print("Button found")
            
            button.click()
            
            WebDriverWait(driver, 60000000000).until(
                EC.presence_of_element_located((By.ID, 'completion_element_id')) 
            )
            
            print("Training Completed")
        
        except Exception as e:
            print(f"Error: {e}")
        
        finally:
            # Clean up and close the browser
            driver.quit()
            
    def evaluate_model(self):
        
        obj = Test()
        obj()
        
    def __call__(self):
        self.federated_preparer()
        self.launch_federated_headless(self.url)
        self.evaluate_model()
        
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(
        prog="Launch Federated"
    )
    
    parser.add_argument("--nb_users", type=int, help="Number of users")
    parser.add_argument("--batch_size", type=int, help="Size of user batch of images")
    parser.add_argument("--mode", type=str, help="How to launch the simulation")
    parser.add_argument("--nb_roc", type=str, help="Number of round of communication")
    parser.add_argument("--lr", type=str, help="Learning rate")
    
    args = parser.parse_args()
    
    obj = Federated(args)
    obj()