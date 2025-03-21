import os
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

GENE_DATABASE_FILE = "info_files/gene_database.txt"
GENE_GROUP_FILE = "info_files/gene_group.txt"
INTERMEDIATE_GENES_FILE = "info_files/intermediate_genes.txt"
UNIDENTIFIABLE_GENE_FILE = "info_files/unidentifiable_genes.txt"
CHANGED_NAME_GENE_FILE = "info_files/changed_name_genes.txt"

GENE_LIST = []
UNIDENTIFIABLE_LIST = []
CHANGED_NAME = {}
GROUP = {}
B_D_PAIR = {}

def readDatabase():
    with open(GENE_DATABASE_FILE) as database_file:
        for line_content in database_file:
            if line_content != "\n":
                gene_info = []
                line_content = line_content.replace(" ", "")
                line_content = line_content.replace(")", "")
                line_content = line_content.replace("\n", "")
                temp_list = line_content.split("-", 1)
                main_gene = temp_list[0]
                connecting_genes_list = temp_list[1].split(",")
                neighbors = {}
                for connecting_gene in connecting_genes_list:
                    name = connecting_gene.split("(")[0]
                    num = float(connecting_gene.split("(")[1])
                    neighbors[name] = num
                gene_info.append(main_gene)
                gene_info.append(neighbors)
                GENE_LIST.append(gene_info)
    database_file.close()

def readUnidentifiable():
    with open(UNIDENTIFIABLE_GENE_FILE) as unidentifiable_file:
        for line_content in unidentifiable_file:
            line_content = line_content.replace(" ", "")
            line_content = line_content.replace("\n", "")
            if line_content != "" and "followinggenescannotbefound" not in line_content:
                UNIDENTIFIABLE_LIST.append(line_content)
    unidentifiable_file.close()

def readChangedName():
    with open(CHANGED_NAME_GENE_FILE) as changed_name_file:
        for line_content in changed_name_file:
            line_content = line_content.replace(" ", "")
            line_content = line_content.replace("\n", "")
            if line_content != "" and "followinggeneshavebeenrenamed" not in line_content:
                orig_name = line_content.split("=>")[0]
                new_name = line_content.split("=>")[1]
                CHANGED_NAME[orig_name] = new_name
    changed_name_file.close()

def writeToDatabase():
    os.system('rm ' + GENE_DATABASE_FILE)
    os.system('touch ' + GENE_DATABASE_FILE)
    database_file = open(GENE_DATABASE_FILE, "w")
    for counter in range(0, len(GENE_LIST)):
        gene_info = GENE_LIST[counter]
        main_gene = gene_info[0]
        connecting_genes_list = gene_info[1]
        line_content = main_gene + " - "
        for key, value in sorted(connecting_genes_list.items()):
            line_content = line_content + key + "(" + str(value) + "), "
        line_content = line_content[:-2]
        database_file.write(line_content + "\n\n")
    database_file.close()

def writeGeneGroups():
    os.system('touch ' + GENE_GROUP_FILE)
    grouping_file = open(GENE_GROUP_FILE, "w")

    groups = ["A", "B", "C", "D"]
    descriptions = ["Input gene that has direct connection with another input gene",
                    "Input gene that is indirectly connected to another input gene, via an intermediate gene",
                    "Input gene that is not directly or indirectly connected to another input gene",
                    "Intermediate gene that connects Group B genes with Group A or other Group B genes"]

    for counter in range(0, len(groups)):
        group_id = groups[counter]
        description = descriptions[counter]
        grouping_file.write("Group " + group_id + ": " + description + "\n")
        grouping_file.write("---\n")
        cluster = getListForGroup(group_id)
        for gene in cluster:
            grouping_file.write(gene + "\n")
        grouping_file.write("\n\n\n")
    grouping_file.close()

def writeIntermediateGenes():
    os.system('touch ' + INTERMEDIATE_GENES_FILE)
    intermediates_file = open(INTERMEDIATE_GENES_FILE, "w")
    if len(B_D_PAIR) != 0:
        intermediates_file = open(INTERMEDIATE_GENES_FILE, "w")
        intermediates_file.write("The following pairings (B Genes : D Genes) indicate that the B Gene requires its respective D Gene to serve as an intermediate gene to connect it to the rest of the map of genes:\n\n")
        sorted_pairs = sorted(B_D_PAIR.items())
        for b_gene, d_gene in sorted_pairs:
            intermediates_file.write(b_gene + " : " + d_gene + "\n")
        intermediates_file.close()
    else:
        os.system('rm ' + INTERMEDIATE_GENES_FILE)

def writeUnidentifiable():
    os.system('touch ' + UNIDENTIFIABLE_GENE_FILE)
    cleaned_unidentifiable_list = []
    for gene in UNIDENTIFIABLE_LIST:
        if gene not in cleaned_unidentifiable_list:
            cleaned_unidentifiable_list.append(gene)
    if len(cleaned_unidentifiable_list) != 0:
        unidentifiable_file = open(UNIDENTIFIABLE_GENE_FILE, "w")
        unidentifiable_file.write("The following genes cannot be found on the online STRING database, and will not be used in this program:\n\n")
        for gene in cleaned_unidentifiable_list:
            unidentifiable_file.write(gene + "\n")
        unidentifiable_file.close()
    else:
        os.system('rm ' + UNIDENTIFIABLE_GENE_FILE)

def writeChangedName():
    os.system('touch ' + CHANGED_NAME_GENE_FILE)
    if not CHANGED_NAME:
        os.system('rm ' + CHANGED_NAME_GENE_FILE)
    else:
        changed_name_file = open(CHANGED_NAME_GENE_FILE, "w")
        changed_name_file.write("The following genes have been renamed, as per the online STRING database:\n\n")
        for key, value in CHANGED_NAME.items():
            changed_name_file.write(key + " => " + value + "\n")
        changed_name_file.close()

def initialize_connections():
    for gene_info in GENE_LIST:
        gene = gene_info[0]
        GROUP[gene] = "C"

def identifyGroupA(gene_list):
    for i in range(0, len(gene_list)):
        gene = gene_list[i][0]
        gene_neighbors = gene_list[i][1]
        for j in range(0, len(gene_list)):
            if i == j:
                continue
            other_gene = gene_list[j][0]
            if other_gene in gene_neighbors.keys():
                GROUP[gene] = "A"

def identifyGroupB(gene_list):
    for i in range(0, len(gene_list)):
        content_list = []
        gene = gene_list[i][0]
        gene_neighbors = gene_list[i][1]

        if GROUP[gene] == "A":
            continue

        for j in range(0, len(gene_list)):
            if i == j:
                continue

            other_gene = gene_list[j][0]
            other_gene_neighbors = gene_list[j][1]

            for inter_gene in gene_neighbors.keys():
                if inter_gene in other_gene_neighbors.keys():
                    if gene_neighbors[inter_gene] > other_gene_neighbors[inter_gene]:
                        content_list.append([other_gene_neighbors[inter_gene], inter_gene, other_gene])
                    else:
                        content_list.append([gene_neighbors[inter_gene], inter_gene, other_gene])

        best_match = max(content_list)

        if GROUP[gene] == "C":
            GROUP[gene] = "B"
            GROUP[best_match[1]] = "D"
            B_D_PAIR[gene] = best_match[1]

def parseInput():
    os.system('clear')
    content = []
    input_genes = []
    input_list = []

    with open("input_files/original_gene_list.txt") as arg_input:
        content = arg_input.readlines()

    for gene in content:
        input_list.append(gene.replace(" ", "").replace("\n", ""))

    for gene in input_list:
        if gene not in input_genes:
            input_genes.append(gene)

    current_gene_list = GENE_LIST

    for gene in input_genes:
        already_present = False
        for iter in range(0, len(current_gene_list)):
            existing_gene = current_gene_list[iter][0]
            if existing_gene == gene:
                already_present = True
                break

        if already_present == False:
            if gene in CHANGED_NAME:
                break
            if gene in UNIDENTIFIABLE_LIST:
                break

            gene_info = []
            gene_neighbors = find_neighbor(gene)

            if gene_neighbors == -1:
                UNIDENTIFIABLE_LIST.append(gene)
            else:
                if isinstance(gene_neighbors, str):
                    correct_gene = gene_neighbors
                    CHANGED_NAME[gene] = correct_gene
                    gene = correct_gene
                    gene_neighbors = find_neighbor(gene)

                gene_info.append(gene)
                if "" in gene_neighbors:
                    time.sleep(1)
                    gene_info.append(find_neighbor(gene))
                else:
                    gene_info.append(gene_neighbors)
                GENE_LIST.append(gene_info)
        GENE_LIST.sort()
        writeToDatabase()

    initialize_connections()
    identifyGroupA(GENE_LIST)
    identifyGroupB(GENE_LIST)

def getListForGroup(group_id):
    cluster = []
    for gene in GROUP:
        if GROUP[gene] == group_id:
            cluster.append(gene)
    return cluster

def find_neighbor(input_gene):
    gene_connectors = {}
    options = FirefoxOptions()
    options.binary_location = '/Applications/Firefox.app/Contents/MacOS/firefox'  # Update the path to your Firefox binary
    driver = webdriver.Firefox(executable_path='/usr/local/bin/geckodriver', options=options)
    driver.get("http://string-db.org/")
    driver.find_element(By.ID, "search").click()
    driver.find_element(By.ID, "primary_input:single_identifier").send_keys(input_gene)
    driver.find_element(By.ID, "species_text_single_identifier").send_keys("Homo sapiens")
    driver.find_element(By.XPATH, "//*[@id='input_form_single_identifier']/div[4]/a").click()
    time.sleep(5)
    page_data = driver.page_source
    time.sleep(5)
    if "Sorry, STRING did not find a protein" in page_data:
        return -1
    if "Please select one" in page_data:
        driver.find_element(By.XPATH, "//*[@id='proceed_form']/div[1]/div/div[2]/a[2]").click()
    time.sleep(15)
    driver.find_element(By.XPATH, "//*[@id='bottom_page_selector_settings']").click()
    driver.find_element(By.XPATH, "//*[@id='bottom_page_selector_legend']").click()
    time.sleep(5)
    page_data = driver.page_source
    time.sleep(5)
    split1 = page_data.split("<td class=\"td_name middle_row first_row last_row\" onclick=")
    split2 = split1[1].split("</td>")
    split3 = split2[0].split("\">")
    correct_gene_name = split3[1]
    if input_gene != correct_gene_name:
        return str(correct_gene_name)
    time.sleep(15)
    driver.find_element(By.XPATH, "//*[@id='bottom_page_selector_table']").click()
    driver.find_element(By.ID, "bottom_page_selector_settings").click()
    driver.find_element(By.XPATH, "//*[@id='standard_parameters']/div/div[1]/div[3]/div[2]/div[2]/div[1]/label").click()
    driver.find_element(By.XPATH, "//select[@name='limit']/option[text()='custom value']").click()
    driver.find_element(By.ID, "custom_limit_input").clear()
    driver.find_element(By.ID, "custom_limit_input").send_keys("500")
    time.sleep(5)
    driver.find_element(By.XPATH, "//*[@id='standard_parameters']/div/div[1]/div[5]/a").click()
    time.sleep(20)
    driver.find_element(By.ID, "bottom_page_selector_table").click()
    driver.find_element(By.XPATH, "//*[@id='bottom_page_selector_legend']").click()
    connectors = driver.find_elements(By.CLASS_NAME, "linked_item_row")
    time.sleep(5)
    for connector in connectors:
        neighbor = str(connector.text.split(' ')[0].split('\n')[0])
        confidence_value = str(connector.text.split(' ')[-1].split('\n')[-1])
        gene_connectors[neighbor] = float(confidence_value)
    driver.quit()
    return gene_connectors

def download_svg(gene_list):
    options = FirefoxOptions()
    options.binary_location = '/Applications/Firefox.app/Contents/MacOS/firefox'  # Update the path to your Firefox binary
    driver = webdriver.Firefox(executable_path='/usr/local/bin/geckodriver', options=options)

    if len(gene_list) < 2:
        return -1

    SVG_STRING = ""
    for gene in gene_list:
        SVG_STRING += gene + "\n"

    driver.get("http://string-db.org/")
    wait = WebDriverWait(driver, 20)

    # Click on the search tab
    search_tab = wait.until(EC.element_to_be_clickable((By.ID, "search")))
    search_tab.click()

    # Click on the "Multiple proteins" form
    multiple_proteins_form = wait.until(EC.element_to_be_clickable((By.ID, "multiple_identifiers")))
    multiple_proteins_form.click()

    # Enter the list of genes
    gene_input = wait.until(EC.presence_of_element_located((By.ID, "primary_input:multiple_identifiers")))
    gene_input.send_keys(SVG_STRING)

    # Enter the species
    species_input = wait.until(EC.presence_of_element_located((By.ID, "species_text_multiple_identifiers")))
    species_input.clear()
    species_input.send_keys("Homo sapiens")

    # Click the search button
    search_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='input_form_multiple_identifiers']/div[5]/a")))
    search_button.click()

    # Wait for the results page to load and display the results
    wait.until(EC.presence_of_element_located((By.ID, "bottom_page_selector_table"))).click()
    wait.until(EC.presence_of_element_located((By.ID, "bottom_page_selector_settings"))).click()

    # Adjust settings
    wait.until(EC.presence_of_element_located((By.ID, "confidence"))).send_keys(" ")
    wait.until(EC.presence_of_element_located((By.ID, "block_structures"))).send_keys(" ")
    driver.find_element(By.XPATH, "//*[@id='standard_parameters']/div/div[1]/div[5]/a").click()

    # Wait for the results to update
    time.sleep(15)
    driver.find_element(By.XPATH, "//*[@id='bottom_page_selector_legend']").click()
    time.sleep(10)
    driver.find_element(By.ID, "bottom_page_selector_table").click()
    time.sleep(25)

    # Download the SVG
    element = driver.find_element(By.XPATH, "//*[@id='bottom_page_selector_table_container']/div/div[2]/div/div[3]/div[2]/a")
    actions = ActionChains(driver)
    actions.move_to_element(element).click().perform()
    time.sleep(30)
    driver.quit()

def main():
    os.system('mkdir -p info_files')
    os.system('touch ' + GENE_DATABASE_FILE)
    os.system('touch ' + UNIDENTIFIABLE_GENE_FILE)
    os.system('touch ' + CHANGED_NAME_GENE_FILE)

    readDatabase()
    readUnidentifiable()
    readChangedName()

    parseInput()

    writeGeneGroups()
    writeIntermediateGenes()
    writeUnidentifiable()
    writeChangedName()

    entire_list = []
    entire_list.extend(getListForGroup("A"))
    entire_list.extend(getListForGroup("B"))
    entire_list.extend(getListForGroup("C"))
    entire_list.extend(getListForGroup("D"))

    download_svg(entire_list)
    os.system('mkdir svg_files')

if __name__ == "__main__":
    main()