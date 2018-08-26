import requests
import urllib
import os
import img2pdf
from pathlib import Path
from bs4 import BeautifulSoup

url = 'https://mangahub.io/search?q='


def start():
    searchTerm = input('Enter the manga name : ')
    mangaURL = url + urllib.parse.quote(searchTerm)
    displayManga(mangaURL)


def retry(searchTerm):
    displayManga(url + urllib.parse.quote(searchTerm))


def displayManga(mangaURL):
    response = requests.get(mangaURL)
    soup = BeautifulSoup(response.content, 'html.parser')
    results = soup.find_all(class_="media-heading")
    if not results:
        print("No results. Try again")
        return start()
    print("{:<4} {:50} {:10} {:20}".format("#", "NAME", "CHAPTERS", "AUTHOR",))
    num = 1
    for result in results:
        name = result.find('a').text
        try:
            author = result.find('small').text
        except AttributeError:
            author = " "
        latestChapter = result.next_sibling.find('a').text
        print("{:<4} {:50} {:10} {:20}".format(num, name, latestChapter, author))
        num += 1
    chooseManga(results)


def chooseManga(results):
    mangaChosen = input("Enter a number to select a manga or enter a name to search again : ")
    try:
        manga = results[int(mangaChosen) - 1]
        displayChapters(manga.find('a').text, manga.find('a')['href'])
    except IndexError:
        print("Index out of bounds. Try again")
        start()
    except ValueError:
        retry(mangaChosen)


def displayChapters(mangaName, mangaURL):
    print(mangaName + " Chapters")
    response = requests.get(mangaURL)
    soup = BeautifulSoup(response.content, 'html.parser')
    chapters = soup.find_all(class_="_287KE list-group-item")
    num = 1
    for chapter in chapters:
        chapterNum = chapter.find(class_="text-secondary _3D1SJ").text
        print("{:<5} Chapter: {:50}".format(num, chapterNum))
        num += 1
    chooseChapters(mangaName, chapters)


def chooseChapters(mangaName, chapters):
    index = input("Enter 'all' for everything, a single number (5), or a range (5-7) for 5,6 and 7 : ")
    try:
        if "all" in index:
            firstIndex = 0
            secondIndex = len(chapters)
        elif "-" in index:
            temp = index.split("-")
            firstIndex = int(temp[0])
            secondIndex = int(temp[1])
        else:
            firstIndex = int(index)
            secondIndex = firstIndex + 1
        for i in range(firstIndex, secondIndex):
            chapter = chapters[i]
            try:
                downloadChapter(mangaName, chapter.find('span').text, chapter.find('a')['href'])
            except OSError:
                print("OSError occured at index : ", index, " on ", mangaName)
    except IndexError:
        print("Invalid Format, try again")
        chooseChapters(mangaName, chapters)


def downloadChapter(mangaName, chapterName, chapterURL):
    response = requests.get(chapterURL)
    soup = BeautifulSoup(response.content, 'html.parser')
    baseImageURL = soup.find_all(class_="PB0mN")[0]['src'].split('1.jpg')[0]
    chapterLength = int(soup.find_all(class_="_3w1ww")[0].text.split('/')[1]) + 1
    folder = Path(mangaName + "//")
    folder.mkdir(parents=True, exist_ok=True)
    imageNames = []
    for num in range(1, chapterLength):
        name = mangaName + " " + chapterName + " " + str(num) + ".jpg"
        imageNames.append((str(folder.resolve()) + "//" + name))
        file = folder.joinpath(name)
        response = requests.get(baseImageURL + str(num) + ".jpg")
        with file.open('wb') as wf:
            wf.write(response.content)
    generatePDF(folder, imageNames, chapterName, mangaName)


def generatePDF(folder, imageNames, chapterName, mangaName):
    file = folder.joinpath(mangaName + " " + chapterName + ".pdf")
    with file.open('wb') as wf:
        wf.write(img2pdf.convert(imageNames))
    for name in imageNames:
        os.remove(name)
    print("Finished with " + chapterName)


if __name__ == '__main__':
    print("Searching for manga on mangahub.io")
    start()


