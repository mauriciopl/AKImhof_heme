from django.http import HttpResponse
from django.template import loader


import seqdhbm.workflow as wf

def index(request):
    cont = 1#wf.workflow(fastafile="/home/imhof_team/Public/mauricio/workflow/ARO2(376)/ARO2(376).fasta" ,mode="structure")
    template = loader.get_template('SeqDHBM/index.html')
    context = {
        'variablename': [1,2,3],
    }
    return HttpResponse(template.render(context, request))

def hemewf(request):
    message=""
    rawseq  = request.GET.get('aaseq')
    """if request.GET.get('fastafile'):
        message += '<p>You submitted: %r</p>' % request.GET['fastafile']
    if request.GET.get('sequence'):
        message += '<p>You submitted: %r</p>' % request.GET['sequence']
    if request.GET.get('aaseq'):
        message += '<p>You submitted: %r</p>' % request.GET['aaseq']
    if request.GET.get('pdbfiles'):
        message += '<p>You submitted: %r</p>' % request.GET['pdbfiles']
    if request.GET.get('pdbids'):
        message += '<p>You submitted: %r</p>' % request.GET['pdbids']
    if request.GET.get('mode'):
        message += '<p>You submitted: %r</p>' % request.GET['mode']"""
    result = wf.workflow(rawseq=rawseq)#fastafile="/home/imhof_team/Public/mauricio/workflow/test.fasta")#
    try:
        message += str(result)
    except Exception as e:
        message += str(e)
    #for fold, sites in result:
    #    message += '<p>fold:%s</p>'%fold
    #    message += '<p>sites:%s</p>'%str(sites)

    return HttpResponse((message if message else "You submitted nothing!"))
