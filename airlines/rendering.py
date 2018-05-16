from django.http import HttpResponse
from django.template import loader
from django.db.models import Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.http import urlencode
from django.shortcuts import redirect
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.db import OperationalError
from django.urls import NoReverseMatch
from django.utils.http import urlquote, urlunquote
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from background_task import background
import os
import json

DEFAULT_PAGE_SIZE     = 30
FLIGHT_EDIT_PAGE_SIZE = 15

from . import static


def argurl(pageName, pageAttrs={}, fullUri=False, uriScheme=None, currentPageName=None, currentPageParams=None, currentPageRequest=None, doNotGenerateBack=False, proxyBack=False, backParams=None, passAttrs=False, passExcept=None):
    if not currentPageParams:
        if currentPageRequest:
            currentPageParams =  currentPageRequest.GET.dict()
    if not currentPageName:
        if currentPageRequest:
            currentPageName = currentPageRequest.resolver_match.view_name
    if not pageName:
        pageName = currentPageName

    reverseURL = '/'
    try:
      reverseURL = reverse(pageName)
      if fullUri:
        if currentPageRequest:
          scheme = currentPageRequest.scheme
          if uriScheme:
            scheme = uriScheme
          reverseURL =  "{0}://{1}{2}".format(scheme, currentPageRequest.get_host(), reverseURL)
    except NoReverseMatch:
        reverseURL = pageName

    if not currentPageParams:
        currentPageParams = {}

    currentPageParamsDup = {
        **currentPageParams
    }

    previousBackParams = currentPageParams.get('back-params', '')
    previousBack = currentPageParams.get('back', '')

    currentPageParamsDup.pop('back-params', None)
    currentPageParamsDup.pop('back', None)

    if passAttrs:
        if not passExcept:
          pageAttrs = {
              **currentPageParams,
              **pageAttrs
          }
        else:
          pageAttrsNew = {}
          for k, v in currentPageParams.items():
            if k not in passExcept:
              pageAttrsNew[k] = v
          pageAttrs = {
            **pageAttrsNew,
            **pageAttrs
          }
          

    currentPageParams = currentPageParamsDup

    backs = {
        # TODO: Switch this to quote bacouse it should be then unquoted :(
        'back-params': urlquote(json.dumps(currentPageParams)),
        'back': currentPageName
    }

    if not proxyBack:
        if doNotGenerateBack:
            backs = {}

    if not reverseURL.endswith('?'):
        reverseURL = reverseURL + '?'

    if proxyBack:
        backs = {
            'back-params': previousBackParams,
            'back': previousBack
        }

    if backParams:
        if not (reverseURL.endswith('?') or reverseURL.endswith('&')):
            reverseURL = reverseURL + '&'
        reverseURL = reverseURL + backParams
        if not (reverseURL.endswith('?') or reverseURL.endswith('&')):
            reverseURL = reverseURL + '&'

    return reverseURL + urlencode({
        **pageAttrs,
        **backs
    })

def getBackURL(request, params={}, proxyBack=False):
    backURL = request.GET.get('back', None)
    backParams = request.GET.get('back-params', None)
    if backParams:
        backParams = json.loads(urlunquote(backParams))
    else:
        backParams = {}

    if proxyBack:
        return argurl(
            backURL,
            {
                **backParams,
                **params
            },
            proxyBack=True,
            currentPageRequest=request
        )
    return argurl(
        backURL,
        {
            **backParams,
            **params
        },
        doNotGenerateBack=True,
        currentPageRequest=request
    )


def useServerStatus(request, context):
  context.update({
    'server_status_url': argurl(
      'serverStatus',
      doNotGenerateBack=True,
      currentPageRequest=request,
      fullUri=True,
      uriScheme='ws'
    )
    
    #request.build_absolute_uri() + '/server_status' #'ws://localhost:8000/airlines/server_status'
  })

    
def paginateContent(pageName, pageAttrs, request, data_list, attr_names, page_size=DEFAULT_PAGE_SIZE):

  global DEFAULT_PAGE_SIZE

  force_empty_page_data = False
  
  page = request.GET.get('page', 1)
  orderby = request.GET.get('orderby', '')
  mode = request.GET.get('mode', '')
  next_page = None
  previous_page = None
  first_page = None
  last_page = None

  orderby_attr_found = False
  for attr in attr_names:
    if orderby == attr:
      data_list = data_list.order_by(attr).reverse()
      orderby_attr_found = True
      break
  if not orderby_attr_found:
    orderby = attr_names[0]

  if mode == 'asc':
    data_list = data_list.reverse()
  elif mode == 'desc':
    mode = 'desc'
  else:
    data_list = data_list.reverse()
    mode = 'asc'

  paginator = Paginator(data_list, page_size)
  page_data = None

  def generatePageLink(pageno, newOrderBy=None, newMode=None, doNotGenerateBack=False):
    
    if not pageno:
      return None
    if not newMode:
      newMode = mode
    if not newOrderBy:
      newOrderBy = orderby

    #if link_has_params:
    #  return pageName+'&page='+str(pageno)+'&orderby='+newOrderBy+'&mode='+newMode
    #return pageName+'?page='+str(pageno)+'&orderby='+newOrderBy+'&mode='+newMode

    return argurl(
        None,
        {
            **pageAttrs,
            'page': str(pageno),
            'orderby': newOrderBy,
            'mode': newMode
        },
        currentPageRequest=request,
        doNotGenerateBack=doNotGenerateBack
    )

  sort_links = {}
  for attr in attr_names:
    sort_links[attr] = {
      'link': generatePageLink(page, attr, 'desc', doNotGenerateBack=True),
      'mode': ''
    }

  if orderby in sort_links:
    sort_links[orderby]['mode'] = 'sort-'+mode
    if mode == 'desc':
      sort_links[orderby]['link'] = generatePageLink(page, orderby, 'asc', doNotGenerateBack=True)

  try:
    page_data = paginator.page(page)
    page = int(page)
    if page < paginator.num_pages:
      next_page = page + 1
    if page > 1:
      previous_page = page - 1
  except PageNotAnInteger:
    page_data = paginator.page(1)
    page = 1
    next_page = 2
  except EmptyPage:
    page_data = paginator.page(paginator.num_pages)
    page = paginator.num_pages
    previous_page = page - 1
  except:
    page_data = []
    force_empty_page_data = True
    
  
  if not force_empty_page_data:  
    if page != 1:
      first_page = 1
    if page != paginator.num_pages:
      last_page = paginator.num_pages

  if not force_empty_page_data:
    pages = [
      {
        'link': generatePageLink(pageno),
        'no': pageno
      } for pageno in paginator.page_range
    ]

    pages_range = 5
    pages_min = page-pages_range
    if pages_min < 0:
      pages_min = 0

    pages_max = page+pages_range
    if pages_max > paginator.num_pages:
      pages_max = paginator.num_pages

    pages = pages[pages_min:pages_max]

    if len(pages) <= 1:
      pages = None
  else:
    pages = None

  return {
    'current_page': page,
    'pages': pages,
    'next_page': generatePageLink(next_page),
    'previous_page': generatePageLink(previous_page),
    'first_page': generatePageLink(first_page),
    'last_page': generatePageLink(last_page),
    'sort_links': sort_links,
    'page_data': page_data
  }

def renderContentTemplate(request, context, template, pageName=None, wrapRequest=True):
  try:
    useServerStatus(request, context)
    if request.user.is_authenticated:
      context.update({
        'user_auth': request.user
      })
    else:
      context.update({
        'user_auth': None
      })
  except:
    context.update({
      'user_auth': None
    })
    
  if pageName:
    context.update({
      'content': pageName
    })
  
  content = template.render(context, request)
  if not wrapRequest:
    return content
  return HttpResponse(content)
  
  
def renderContentPage(pageName, request, data_list, attr_list, mapping=None):
  context = paginateContent(pageName, {}, request, data_list, attr_list)
  template = loader.get_template('index.html')
  context.update({
    'content': pageName
  })
  try:
    if request.user.is_authenticated:
      context.update({
        'user_auth': request.user
      })
    else:
      context.update({
        'user_auth': None
      })
  except:
    context.update({
      'user_auth': None
    })
    
  if mapping:
      context = mapping(context)
      
  useServerStatus(request, context)
  return renderContentTemplate(request, context, template)
  
  
@background(schedule=0)
def generateStaticPages():
  print('[STATIC_RENDER] Render static pages')
  pages = static.staticPages()
  if not pages:
    print('[STATIC_RENDER] Nothing to render. Quit')
    return
  
  for page in pages:
    print('[STATIC_RENDER] Render static page: '+page)
    content = renderContentTemplate(
      None,
      {},
      loader.get_template('index.html'),
      pageName=page,
      wrapRequest=False
    )
    
    filename = static.getPagePath(page)
    print('[STATIC_RENDER] Saving rendered static page to "'+filename+'"')
    
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w+') as f:
      f.write(content)
    print('[STATIC_RENDER] Saved')
  print('[STATIC_RENDER] Rendered all pages.')
  
def renderStaticPage(page):
  filename = static.getPagePath(page)
  content = ''
  with open(filename) as f:
    content = f.read()
  return HttpResponse(content)
