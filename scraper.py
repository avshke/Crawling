import requests, re, json
from bs4 import BeautifulSoup

MAX_ITEMS = 300
PAGE_THRESHOLD = 20

def scrap_item(page, id_counter, link):
    parser = BeautifulSoup(page, 'html.parser')
    num_data = parser.find("div", {"class": "summary-stats-box"}).get_text()
    num_data = re.sub('\s+', ' ', num_data)
    num_data = num_data.split("|")
    ing_lst = []
    direc_lst = []
    for ele in parser.findAll("span", {"class": "recipe-ingred_txt added"}):
        ing_lst.append(ele.text)
    for el in parser.findAll("span", {"class": "recipe-directions__list--item"}):
        direc_lst.append(el.text)

    times_lst = parser.find("ul", {"class": "prepTime"}).text
    times_lst = re.sub('\n+', '\n', times_lst)

    scrap_dic = {
        "id": id_counter,
        "url": link,
        "Title": parser.title.text[:-24],
        "Creator": parser.find("span", {"class": "submitter__name"}).text,
        "Rating": parser.find("div", {"class": "rating-stars"})["data-ratingstars"],
        "NumMadeIt": num_data[0].split(" ")[1],
        "NumReviews": num_data[1].split(" ")[1],
        "NumPhotos": num_data[2].split(" ")[1],
        "Ingredients": ing_lst,
        "Directions": direc_lst,
    }
    if len(times_lst) > 3:
        times_lst = re.sub('["Cook","Ready In","Prep"]', "", times_lst).split('\n')
        scrap_dic["PrepTime"] = times_lst[1]
        scrap_dic["CookTime"] = times_lst[2]
        scrap_dic["ReadyTime"] = times_lst[3]
    else:
        scrap_dic["PrepTime"] = scrap_dic["CookTime"] = scrap_dic["ReadyTime"] = None
    return scrap_dic


def scrape_pages(max_pages, page_counter):
    all_dict = []
    base_url = "https://www.allrecipes.com/recipes/156/bread/"
    page_add = "?page="
    page = 1
    while page <= max_pages and len(all_dict) < MAX_ITEMS:
        page_txt = requests.get(base_url + page_add + str(page)).text
        beauty_parse = BeautifulSoup(page_txt, 'html.parser')
        for recipe in beauty_parse.findAll("div", {"class": "fixed-recipe-card__info"}):
            page_counter += 1
            link = recipe.select_one('a')["href"]
            if link is not None:
                link_txt = requests.get(link).text
                item_dict = scrap_item(link_txt, page_counter, link)
                all_dict.append(item_dict)
        page += 1

    records = {"record": all_dict}
    with open('dataFile.json', 'w') as outfile:
        json.dump(records, outfile, indent=4)


def main():
    scrape_pages(PAGE_THRESHOLD, 0)

if __name__ == '__main__':
    main()