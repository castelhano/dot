@login_required
@permission_required('trafego.add_planejamento')
def planejamento_add(request):
    if request.method == 'POST':
        form = PlanejamentoForm(request.POST)
        if form.is_valid():
            try:
                registro = form.save(commit=False)
                registro.usuario = request.user
                registro.save()
                l = Log()
                l.modelo = "trafego.planejamento"
                l.objeto_id = registro.id
                l.objeto_str = registro.codigo
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,'Planejamento <b>' + registro.codigo + '</b> criado')
                return redirect('trafego_planejamento_id', registro.id)
            except:
                messages.error(request,'Erro ao inserir planejamento')
                return redirect('trafego_planejamento_add')
    else:
        form = PlanejamentoForm()
    return render(request,'trafego/planejamento_add.html',{'form':form})
    

@login_required
@permission_required('trafego.change_planejamento')
def planejamento_id(request,id):
    planejamento = Planejamento.objects.get(pk=id)
    form = PlanejamentoForm(instance=planejamento)
    return render(request,'trafego/planejamento_id.html',{'form':form,'planejamento':planejamento})
    
    
@login_required
@permission_required('trafego.change_planejamento')
def planejamento_update(request,id):
    planejamento = Planejamento.objects.get(pk=id)
    form = PlanejamentoForm(request.POST, instance=planejamento)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "trafego.planejamento"
        l.objeto_id = registro.id
        l.objeto_str = registro.codigo
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,'Planejamento <b>' + registro.codigo + '</b> alterado')
        return redirect('trafego_planejamento_id', id)
    else:
        return render(request,'trafego/planejamento_id.html',{'form':form,'planejamento':planejamento})
        
        
@login_required
@permission_required('trafego.delete_planejamento')
def planejamento_delete(request,id):
    try:
        registro = Planejamento.objects.get(pk=id)
        l = Log()
        l.modelo = "trafego.planejamento"
        l.objeto_id = registro.id
        l.objeto_str = registro.codigo
        l.usuario = request.user
        l.mensagem = "DELETE"
        l.save()
        registro.delete()
        messages.warning(request,'Planejamento apagado. Essa operação não pode ser desfeita')
        return redirect('trafego_planejamentos')
    except:
        messages.error(request,'ERRO ao apagar planejamento')
        return redirect('trafego_planejamento_id', id)