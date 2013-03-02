#!/usr/bin/python
#coding: utf-8

import socket
import sys
import threading
import functools
import settings


def Decorator_funcoes():
    class _Decorator_funcoes(object):
        def __init__(self, fn):
            self.fn = fn

        def __get__(self, obj, type=None):
            return functools.partial(self, obj)

        def __call__(self, *args, **kwargs):
            #threading.Thread(target=self.fn, args=args).start()
            return self.fn(*args)

    return _Decorator_funcoes

def Decorator_requisita():
    class _Decorator_requisita(object):
      def __init__(self, fn):
          self.fn = fn

      def __get__(self, obj, type=None):
          return functools.partial(self, obj)

      def __call__(self, *args, **kwargs):
        tipo = args[1]
        print '\033[0;32mPerguntando quem tem a operação: \033[1;33m{}\033[0m'.format(tipo)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(1)
        endereco = (settings.SERVIDOR_DNS_IP, settings.SERVIDOR_DNS_PORTA)
        try:
            s.sendto(tipo, endereco)
            resposta, endereco = s.recvfrom(args[0].MAX_PACOTE)
        except socket.timeout:
            print '\033[1;31mServidor DNS desconectado\033[0m'
            return settings.SERVIDOR_ERRO
        except socket.error:
            print '\033[1;31mFalha na conexão com o Servidor DNS\033[0m'
            return settings.SERVIDOR_ERRO
        if resposta == settings.DNS_ERRO_MSG:
          print '\033[0;32mOperação \033[1;33m{} \033[0;32minexistente\033[0m'.format(tipo)
          return settings.DNS_ERRO_MSG
        else:
          ip_servidor_operacoes = resposta
          print '\033[1;33m{} \033[0;32mtem a operação \033[1;33m{}\033[0m'.format(ip_servidor_operacoes, tipo)
          resultado = self.fn(args[0], args[1], args[2], ip_servidor_operacoes)
          if resultado == settings.SERVIDOR_ERRO:
            print '\033[1;31mServidor de Operações retornou erro\033[0m'
          return resultado

    return _Decorator_requisita


class Operacoes(object): 
  def __init__(self, servidor_dns_ip):
    self.servidor_dns_ip = servidor_dns_ip
    self.porta = settings.CLIENTE_PORTA
    self.MAX_PACOTE = 1024
  
  @Decorator_funcoes()
  def subtracao(self, x, y):
    tipo = settings.OPERACOES['subtracao']['nome']
    resultado = self.requisita(tipo, (x, y))
    return resultado

  @Decorator_funcoes()
  def soma(self, x, y):
    tipo = settings.OPERACOES['soma']['nome']
    resultado = self.requisita(tipo, (x, y))
    return resultado

  @Decorator_funcoes()
  def produto(self, x, y):
    tipo = settings.OPERACOES['produto']['nome']
    resultado = self.requisita(tipo, (x, y))
    return resultado

  @Decorator_funcoes()
  def divisao(self, x, y):
    tipo = settings.OPERACOES['divisao']['nome']
    resultado = self.requisita(tipo, (x, y))
    return resultado

  @Decorator_funcoes()
  def fatorial(self, x):
    tipo = settings.OPERACOES['fatorial']['nome']
    resultado = self.requisita(tipo, (x))
    return resultado

  @Decorator_requisita()
  def requisita(self, tipo, args, servidor_ip=None):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    endereco = (servidor_ip, self.porta)
    try:
        s.connect(endereco)
    except socket.timeout:
        print '\033[1;31mFalha na conexão com o Servidor de Operações \033[1;33m{}'.format(servidor_ip)
        return settings.SERVIDOR_ERRO
    except socket.error:
        print '\033[1;31mFalha na conexão com o Servidor de Operações \033[1;33m{}'.format(servidor_ip)
        return settings.SERVIDOR_ERRO
    if(len(args) == 1):
      tipo = "{} {}".format(tipo, *args)
    elif(len(args) == 2):
      tipo = "{} {} {}".format(tipo, *args)
    print '\033[0;32mRequisitando \033[1;33m{} \033[0;32mpara \033[1;33m{} \033[0m'.format(tipo, endereco[0])
    try:
        s.send(tipo)
        dados = s.recv(self.MAX_PACOTE)
    except socket.timeout:
        print '\033[1;31mFalha na conexão com o Servidor de Operações \033[1;33m{}'.format(servidor_ip)
        return settings.SERVIDOR_ERRO
    except socket.error:
        print '\033[1;31mFalha na conexão com o Servidor de Operações \033[1;33m{}'.format(servidor_ip)
        return settings.SERVIDOR_ERRO

    #dados = ''
    #dado, endereco = s.recvfrom(self.MAX_PACOTE)
    #while dado != 'FIM':
    #  dados += dado
    #  dado, _ = s.recvfrom(self.MAX_PACOTE)
    return dados


if __name__=='__main__':
    print '\033[0;34m === Cliente iniciado ===\033[0m'
    print ''
    operacoes = Operacoes(settings.CLIENTE_IP)
    print '\033[0;32mOperações Disponíveis:\033[0m'
    for operacao in settings.OPERACOES.keys():
        print '\033[1;33m{}\033[0m'.format(settings.OPERACOES[operacao]['nome'])
    print ''

    try:
        while True:
            operacao = raw_input('\033[0;32mOperação: \033[0m')
            if operacao in settings.OPERACOES:
                dados_operacao = settings.OPERACOES[operacao]
                valores = []
                for i in xrange(dados_operacao['num_args']):
                    valores.append(raw_input('\033[0;32m{}º valor: \033[0m'.format(i+1)))
                resultado = operacoes.__getattribute__(dados_operacao['funcao'])(*valores)
                if resultado != settings.SERVIDOR_ERRO and resultado != settings.DNS_ERRO_MSG:
                    if len(valores) == 1:
                        print '\033[0;32m{} de \033[1;33m{} \033[0;32mé \033[1;33m{}\033[0m'.format(dados_operacao['nome'], valores[0], resultado)
                    else:
                        valores = '\033[0;32m e \033[1;33m'.join(valores)
                        print '\033[0;32m{} de \033[1;33m{} \033[0;32mé \033[1;33m{}\033[0m'.format(dados_operacao['nome'], valores, resultado)
                else:
                    pass
            else:
                print '\033[0;32mOperação \033[1;33m{} \033[0;32minexistente\033[0m'.format(operacao)
            print ''
    except KeyboardInterrupt:
        print '\n\033[0;34m === Cliente finalizado ===\033[0m'
        exit()
    
  
