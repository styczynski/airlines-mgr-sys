from .forms import FilterFlightsForm


def staticPages():
  return [
    'crews-panel'
  ]
  
def getPagePath(page):
  return './staticfiles/airlines-static/' + page + '.html'
  
def getPageContext(page):
  return {
    'filter_form': FilterFlightsForm()
  }