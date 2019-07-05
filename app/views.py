#render for rendring template and response back it to user.
from django.shortcuts import render
from django.http import HttpResponse

#model for movies
from .models import Movies

#if not data found in database for particular id
from django.core.exceptions import ObjectDoesNotExist

#if pagination handling
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

#for json conversion of data
import json

# for regex match
import re

# import beautifulsoap and get for scraping the movies
from bs4 import BeautifulSoup
from requests import get


# Its homepage view
def homepage(request):
    return render(request, "pages/index.html")


#all movies page
def movies(request):
    # in production never do this :P, We should not fetch whole rows to paginate. 
    movie_list = Movies.objects.all()
    if(Movies.objects.count()) :
        page = request.GET.get('page', 1)
        paginator = Paginator(movie_list, 10)

        try:
            movie_list = paginator.page(page)
        except PageNotAnInteger:
            movie_list = paginator.page(1)
        except EmptyPage:
            movie_list = paginator.page(paginator.num_pages)

    return render(request, "pages/movies.html", {"movies": movie_list, "movies_count": Movies.objects.count()})


# movie page view
def movie(request,prime_id):
    try:
        movi = Movies.objects.get(prime_id=prime_id)
        return render(request, "pages/movie.html", {"movie":movi})
    except ObjectDoesNotExist:
        return HttpResponse("Can't find any data for id " + str(prime_id) + "!")

def movie_filter(reequest):
    return render(reequest, "pages/movies_filter.html")


# autcomplete ajax method
def movies_ajax_search(request):
    q = request.GET.get('term', '').capitalize()

    search_qs = Movies.objects.filter(name__startswith=q).order_by('-rating')
    results = []
    for r in search_qs:
        results.append({
            "prime_id": r.prime_id,
            "name": r.name,
            "release_date": r.release_date,
            "rating": r.rating,
        })
    return HttpResponse(json.dumps(results), 'application/json')
    

# data scraping
def scrap(request):
    page_no = request.GET.get("page_no",0)
    calculated = 0

    # check is client provided any page_no or not
    if(int(page_no) > 0):
        calculated = (50*int(page_no)) + 1

    # Here 100 is limit you can increase
    if(Movies.objects.all().count() < 100):
        url = "https://www.imdb.com/search/title/?release_date=2019&start="+ str(calculated) +"&ref_=adv_nxt"
        resp = get(url)

        html_soup = BeautifulSoup(resp.text, 'html.parser')
        type(html_soup)
        movie_containers = html_soup.find_all('div', class_ = 'lister-item mode-advanced')

        # Lists to store the scraped data in
        names = []
        descriptions = []
        years = []
        imdb_ratings = []
        metascores = []
        votes = []

        # Extract data from individual movie container
        for container in movie_containers:

            # If the movie has Metascore, then extract:
            if container.find('div', class_ = 'ratings-metascore') is not None:
                name = container.h3.a.text
                names.append(name)

                # The year
                year = container.h3.find('span', class_ = 'lister-item-year').text
                years.append(year[year.rfind("(")+1:year.rfind(')')])

                # The IMDB rating
                imdb = float(container.strong.text)
                imdb_ratings.append(imdb)

                # The Metascore
                m_score = container.find('span', class_ = 'metascore').text
                metascores.append(int(m_score))

                # The number of votes
                vote = container.find('span', attrs = {'name':'nv'})['data-value']
                votes.append(int(vote))

                # The description
                description = container.find("div", class_='ratings-bar').find_next('p')
                descriptions.append(description.text)
        
        for i in range(0,len(names)):
            Movies.objects.create(name=names[i],
                        description=descriptions[i],
                        release_date= years[i],
                        rating= imdb_ratings[i],
                        votes=votes[i],
                        meta_score= metascores[i])

        return render(request, "pages/scrap.html", {"page_no": int(page_no)+1})
    else:
        return HttpResponse("Our Work is Done Now!")