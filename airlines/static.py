#
# Static files declarations for airlines management sysyem
# MIT Piotr Styczyński 2018
#
from .forms import FilterFlightsForm

#
# Define static pages' names to be rendered at Django startup
#
def staticPages():
    return [
        'crews-panel'
    ]

#
# Obtain template path from static page name returned by staticPages()
#
def getPagePath(page):
    return './staticfiles/airlines-static/' + page + '.html'

#
# Obtain template additional context by page name returned by staticPages()
#
def getPageContext(page):
    return {
        'filter_form': FilterFlightsForm()
    }
