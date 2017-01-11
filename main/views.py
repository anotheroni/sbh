# coding: utf-8
import re   # regexp
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from sbh.main.models import GasStation, UserAuth

@login_required()
def program_list(request):
  station_list = UserAuth.objects.filter(user = request.user)
  c = RequestContext(request, {'object_list': station_list})
  return render_to_response('main/program_list.html', c)

