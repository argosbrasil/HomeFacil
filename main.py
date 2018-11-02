# -*- coding:UTF-8 -*-

import kivy
kivy.require('1.10.1')
# bibliotecas python
import serial

# bibliotecas kivy
from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.storage.jsonstore import JsonStore
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.properties import StringProperty, ObjectProperty, NumericProperty, ListProperty, BooleanProperty
from kivy.uix.modalview import ModalView
from kivy.uix.button import Button

__version__ = "0.0.1.0"
__author__ = "Jose Egidio Agostinho"

#  ###########################################################################
# -------------------------------------------------------------------------------
# Name:         homefacil
# Purpose:      Aplicativo IoT Home
#               Compativel com smartphones e tablets Android, iPhone, iPad, e
#               Windows 8 Mobile.
#               Compativel com GNU/Linux, Windows e OS X.
#               Comando compilacao : buildozer --profile demo android debug
#		        buildozer android debug deploy debug
# Author:       Jose Egidio Agostinho
#
# Created:      09-10-2018
# Copyright:   © Jose Egidio Agostinho: 2018
# Licence:     Propria
# -------------------------------------------------------------------------------
# Configuracao Arduino
# A0, A1, A2, A3, A4, A5 -> Sensores de Temperatura e Umidade DHT11
#
# D2 - Out -> Sirene
# D3 - Out -> Cerca Eletrica
# D4 - Out -> Iluminação Externa 1
# D5 - Out -> Iluminação Externa 2
# D6 - Out -> Portao Garagem
# D7 - Inp -> Sensor Ext 1
# D8 - Inp -> Sensor Ext 2
# D9 - Inp -> Sensor Mov 1
# D10 - In -> Sensor Mov 2
# D11 - In -> Sensor Mov 3
# D12 - In -> Sensor Mov 4
# ###########################################################################


# Montador utilizado para carregar os arquivos kv no main.py
lst_kv_loaded_second = ['kv/abertura.kv', 'kv/home.kv']

for r in lst_kv_loaded_second:
    Builder.load_file(r)


# ###########################################################################
_txt_informacao = 'Parabéns por adquirir um produto Argos, elaborado com tecnologia de '
_txt_informacao += 'última geração.\n\n'
_txt_informacao += 'Este é um manual de utilização simplificado para uso diário, sugerimos '
_txt_informacao += 'que em caso de dúvida consulte o manual do usuário que acompanha este '
_txt_informacao += 'produto.\n\n'
_txt_informacao += 'Sobre o Sistema HomeFacil\n\n'
_txt_informacao += 'O Sistema HomeFacil foi desenvolvido para uso residencial e comercial, '
_txt_informacao += 'e tem como objetivo o controle de rotinas como iluminação automática, '
_txt_informacao += 'monitoramento de zonas de segurança, acesso, temperatura e umidade e '
_txt_informacao += 'simulação de presença.\n\n'
_txt_informacao += 'O Sistema HomeFacil é composto por um tablet, módulo de controle e aplicativos '
_txt_informacao += 'necessários para o seu funcionamento, o aplicativo de controle pode '
_txt_informacao += 'ser instalado em smartphones e é comercializado independentemente do Sistema HomeFacil.\n\n'
_txt_informacao += 'O Sistema HomeFacil pode ser configurado para controlar a temperatura/umidade do ambiente, '
_txt_informacao += 'ligar/desligar aparelhos de resfriamento, umidificadores e aquecedores, iluminação '
_txt_informacao += 'interna e externa, controle de acesso como portas e portões, aparelhos de mídia como televisores, '
_txt_informacao += 'equipamentos de áudio e monitoramento de áreas externas e internas.\n\n'
_txt_informacao += 'O Sistema HomeFacil apresenta em seu "display" monitoração de temperatura e '
_txt_informacao += 'umidade, "status" de monitoração de áreas externas e internas e alarme, botão de pânico, '
_txt_informacao += 'acesso aos controles de iluminação, acesso e multimídia. Apresenta, também, '
_txt_informacao += 'informações por meio de uma planta do imóvel em 2D, opcionalmente em 3D.\n\n'
_txt_informacao += 'O Sistema HomeFacil apresenta link de comunicação remoto via WIFI para servidores de '
_txt_informacao += 'monitoramento, comunicação intermodulos por meio de "BT/RS485/USB".'
#  ###########################################################################

def mainthread(func):
    	def delayed_func(*args, **kwargs):
		def callback_func(dt):
			func(*args, **kwargs)

		Clock.schedule_once(callback_func, 0)

	return delayed_func

#  ###########################################################################

# classe página de abertura
class Abertura(Screen):

    name_mv = StringProperty()
    txt_cabecalho = StringProperty()
    tst_cad_acess = BooleanProperty(True)


    acesso = JsonStore('json/acesso.json')
    if len(acesso) <= 1: tst_cad_acess = False

    def __init__(self, **kwargs):
        super(Abertura, self).__init__(**kwargs)
        self.init_abertura()

    def init_abertura(self):
        self.name_mv = 'imagens/mv_splash/teste.gif'

class KbDesbloqueio(ModalView):

    txt_cabecalho = StringProperty('DIGITE CÓDIGO DE ACESSO PARA CANCELAR ALARME')
    txt_acesso_usu_view = StringProperty()
    txt_acesso_sys = ''
    acesso_confirmado = BooleanProperty(False)

    conta_tentativas = NumericProperty(0)

    acesso = JsonStore('json/acesso.json')

    if len(acesso) <= 1:
        tst_cad_acess = False
        txt_cabecalho = 'DIGITE CÓDIGO DE ACESSO PARA CANCELAR ALARME'

    def kb_keypress(self, keypressed):
        st_sys = JsonStore('json/status.json')
        if self.conta_tentativas <= 3:
            self.txt_cabecalho = 'DIGITE CÓDIGO DE ACESSO PARA CANCELAR ALARME'
            if len(self.txt_acesso_sys) != 6:
                self.txt_acesso_sys = self.txt_acesso_sys + keypressed
                self.txt_acesso_usu_view = self.txt_acesso_usu_view + '*'
                if len(self.txt_acesso_sys) == 6:
                    if self.consulta_acesso(self.txt_acesso_sys):
                        self.acesso_confirmado = True
                        self.txt_cabecalho = 'PRESSIONE "CONFIRMA" PARA CANCELAR ALARME'
                        self.conta_tentativas = 0
                        if self.conta_tentativas <= 3 and self.acesso_confirmado:
                            st_sys.put('alrm', st=1)
                            self.dismiss()
                    else:
                        self.acesso_confirmado = False
                        self.txt_cabecalho = 'CÓDIGO INVÁLIDO'
                        self.txt_acesso_usu_view = ''
                        self.txt_acesso_sys = ''
                        self.conta_tentativas += 1
                        st_sys.put('alrm', st=2)
                        if self.conta_tentativas > 3:
                            st_sys.put('alrm', st=3)
                            self.dismiss()
        else:
            self.dismiss()

    def consulta_acesso(self, codigo_acesso):
        if self.acesso.exists(codigo_acesso):
            self.txt_cabecalho = 'PRESSIONE "CONFIRMA" PARA CACELAR ALARME'
            return True
        else:
            self.txt_cabecalho = 'CÓDIGO INVÁLIDO'
            return False

    def ajusta_st_alr_desbloqueio(self):
        
        st_sys = JsonStore('json/status.json')

        print st_sys.get('alrm')['st'], self.acesso_confirmado, self.conta_tentativas

        if st_sys.get('alrm')['st'] == 2 and self.conta_tentativas > 3:
            st_sys.put('alrm', st=3)
            self.dismiss()
        elif st_sys.get('alrm')['st'] == 1 and self.acesso_confirmado and self.conta_tentativas <= 3:
            st_sys.put('alrm', st=1)
            self.dismiss()
        elif st_sys.get('alrm')['st'] == 2 and self.acesso_confirmado and self.conta_tentativas <= 3:
            st_sys.put('alrm', st=1)
        elif st_sys.get('alrm')['st'] == 2 and not self.acesso_confirmado and self.conta_tentativas <= 3:
            st_sys.put('alrm', st=2)
    
##################################################################################


class KbPriAcesso(ModalView):

    txt_cabecalho = StringProperty()
    txt_acesso_usu_view = StringProperty()
    txt_acesso_sys = ''
    acesso_confirmado = BooleanProperty(False)

    acesso = JsonStore('json/acesso.json')

    if len(acesso) <= 1:
        tst_cad_acess = False
        txt_cabecalho = 'CADASTRE O CÓDIGO DE ACESSO COM 6 DIGITOS'

    def kb_priacesso(self, keypressed):
        self.txt_cabecalho = 'CADASTRE O CODIGO DE ACESSO DE 6 DIGITOS'
        if len(self.txt_acesso_sys) != 6:
            self.txt_acesso_sys = self.txt_acesso_sys + keypressed
            self.txt_acesso_usu_view = self.txt_acesso_usu_view + '*'
            if len(self.txt_acesso_sys) == 6:
                if self.cadastro_acesso(self.txt_acesso_sys):
                    self.acesso_confirmado = True
                    self.txt_cabecalho = 'PRESSIONE "CONFIRMA" PARA ABRIR O SISTEMA'
                else:
                    self.acesso_confirmado = False
                    self.txt_cabecalho = 'CÓDIGO INVÁLIDO'

    def consulta_acesso(self, codigo_acesso):
        if self.acesso.exists(codigo_acesso):
            self.txt_cabecalho = 'PRESSIONE "CONFIRMA" PARA ABRIR O SISTEMA'
            return True
        else:
            self.txt_cabecalho = 'CÓDIGO INVÁLIDO'
            return False

    def cadastro_acesso(self, codigo_acesso):
        self.acesso.put(codigo_acesso, codigo=codigo_acesso, nivel='5')
        return self.consulta_acesso(codigo_acesso)


class KbAcesso(ModalView):
    
    txt_cabecalho = StringProperty()
    txt_acesso_usu_view = StringProperty()
    txt_acesso_sys = ''
    acesso_confirmado = BooleanProperty(False)

    acesso = JsonStore('json/acesso.json')

    if len(acesso) > 1:
        tst_cad_acess = True
        txt_cabecalho = 'DIGITE CÓDIGO DE ACESSO PARA ABRIR O SISTEMA'

    def kb_keypress(self, keypressed):
        self.txt_cabecalho = 'DIGITE CÓDIGO DE ACESSO PARA ABRIR O SISTEMA'
        if len(self.txt_acesso_sys) != 6:
            self.txt_acesso_sys = self.txt_acesso_sys + keypressed
            self.txt_acesso_usu_view = self.txt_acesso_usu_view + '*'
            if len(self.txt_acesso_sys) == 6:
                if self.consulta_acesso(self.txt_acesso_sys):
                    self.txt_cabecalho = 'PRESSIONE "CONFIRMA" PARA ABRIR O SISTEMA'
                    self.acesso_confirmado = True
                else:
                    self.txt_cabecalho = 'CÓDIGO INVÁLIDO'
                    self.acesso_confirmado = False
                    self.txt_acesso_sys = ''
                    self.txt_acesso_usu_view = ''


    def consulta_acesso(self, codigo_acesso):
        if self.acesso.exists(codigo_acesso):
            self.txt_cabecalho = 'PRESSIONE "CONFIRMA" PARA ABRIR O SISTEMA'
            return True
        else:
            self.txt_cabecalho = 'CÓDIGO INVÁLIDO'
            return False

class Informacao(ModalView):
    global _txt_informacao

    txt_informacao = StringProperty('')
    txt_informacao = _txt_informacao

class SetUpAlrm(ModalView):
    pass

##################################################################################

# classe página home para usuário condômino
class Home(Screen):
    temperatura_indicada = NumericProperty()
    umidade_indicada = NumericProperty()
    temperatura_lida = NumericProperty()
    umidade_lida = NumericProperty()
    temperatura_sp = NumericProperty(24)
    umidade_sp = NumericProperty(40)
    plant_run_img = StringProperty()
    open_local = NumericProperty(1)
    msg_rodape = StringProperty('INICIALIZANDO SISTEMAS')
    cl_msg_rodape = ListProperty([0.46,0.96,0.96,1])

    mv_alrm = StringProperty()

    status_alrm = NumericProperty()

    store = JsonStore('json/ascii.json')
    
    msg_alr_serial = ''
    msg_sens_th = ''

    alr_st_img = StringProperty()
    alr_st = 0
    panic_bt = False
    cerca_bt = False

    cor_indicador_t = ListProperty([0,0,1,1])
    cor_indicador_u = ListProperty([1,0,0,1])
    cor_fundo_indicador = ListProperty([0.83,0.90,0.97,1])

    conta_leitura_indicadores = 0
    conta_leitura_th = 0

    ctrl_plant = 1
    teste_serial = True
    ser = ''

    umid = 0
    temp = 0

    def abertura(self):
        self.check_comm()
        self.init_system()
        Clock.unschedule(self.loop_principal)
        Clock.schedule_interval(self.loop_principal, 0.1)

    def check_comm(self):
        try:
            self.ser = serial.Serial('/dev/ttyUSB1', 115200, timeout=1)
            self.alr_st_img = 'imagens/diversos/usb.png'
            self.msg_alr_serial = ''
            self.teste_serial = True
        except Exception, e:
            print e
            self.alr_st_img = 'imagens/diversos/usb_vm.png'
            self.msg_alr_serial = 'FALHA DE COMUNICACAO INTERMODULOS'
            self.teste_serial = False
            #print self.ser.isOpen

    def inc_temperatura(self):
        self.temperatura_sp += 1

    def inc_umidade(self):
        self.umidade_sp += 1

    def dec_temperatura(self):
        self.temperatura_sp -= 1

    def dec_umidade(self):
        self.umidade_sp -= 1

    def alerta(self):
        pass

    def loop_principal(self, dt):
        try:
            self.check_comm()
            self.atualiza_indicadores_temp_umid()
            self.ctrl_plant()
            self.trata_msg()
            self.status_alarme()
        except Exception, e:
            print e

    # Rotinas do alarme de seguranca
    @mainthread
    def status_alarme(self):
        st_sys = JsonStore('json/status.json')
        try:
            if st_sys.get('alrm')['st'] == 1:
                self.mv_alrm = 'imagens/mv_alrm/mvalr1.gif'
                # Rotina desabilita sensores alarmes
                if self.panic_bt: #Desabilita pânico
                    self.panic_bt = False
                    st_sys.put('panico', st=False)
                    command_line = 'A0PR'
                    write_data = self.ser.write(command_line)

            elif st_sys.get('alrm')['st'] == 2:
                self.mv_alrm = 'imagens/mv_alrm/mvalr2.gif'
                # Rotina habilita sensores alarme
                if self.read_st_sens_alr(): 
                    st_sys.put('alrm', st=3)
                    # Rotina le sensores
            elif st_sys.get('alrm')['st'] == 3:
                self.mv_alrm = 'imagens/mv_alrm/mvalr3.gif'
                # Rotina dispara alarme
        except:
            st_sys.put('alrm', st=1)

    @mainthread
    def panic(self):
        st_sys = JsonStore('json/status.json')
        self.panic_bt = True
        st_sys.put('alrm', st=3)
        st_sys.put('panico', st=True)
        command_line = 'A0PW'
        write_data = self.ser.write(command_line)

    @mainthread
    def cerca_eletrica(self):
        st_sys = JsonStore('json/status.json')
        self.cerca_bt = True
        st_sys.put('cerca_eletrica', st=True)
        command_line = 'A0CW'
        write_data = self.ser.write(command_line)


    def le_st_alr(self):
        st_sys = JsonStore('json/status.json')
        return st_sys.get('alrm')['st']

    @mainthread
    def es_st_alr(self):
        st_sys = JsonStore('json/status.json')
        if st_sys.get('alrm')['st'] == 1:
            command_line = 'A0PR'
            write_data = self.ser.write(command_line)
        elif (st_sys.get('alrm')['st'] == 2 or st_sys.get('alrm')['st'] == 3):
            pass

    def ajusta_st_alr(self, t):
        st_sys = JsonStore('json/status.json')
        st_sys.put('alrm', st=t)


    def read_st_sens_alr(self):
        '''
        command_line = 'A0AR'
        write_data = self.ser.write(command_line)
        line = self.ser.readline()
        print line
        '''
        return False

    def trata_msg(self):
        if self.msg_alr_serial != '':
            self.msg_rodape = self.msg_alr_serial
            self.cl_msg_rodape = [1,0,0,1]
        elif self.msg_sens_th != '':
            self.msg_rodape = self.msg_sens_th
            self.cl_msg_rodape = [1,0,0,1]
        else:
            self.msg_rodape = 'TODOS OS SISTEMAS OPERACIONAIS'
            self.cl_msg_rodape = [0.46,0.96,0.96,1 ]

    def ctrl_plant(self):
        st_sys = JsonStore('json/status.json')
        try:
            if st_sys.get('alrm')['st'] != 0:
                if self.open_local == 1:
                    self.plant_run_img = 'imagens/planta_baixa/planta1-1.gif'
                elif self.open_local == 0:
                    self.plant_run_img = 'imagens/planta_baixa/planta1.gif'
        except:
            pass

    def atualiza_indicadores_temp_umid(self):
        try:
            self.le_temp_umid()

            self.conta_leitura_indicadores = 0

            self.temperatura_lida = int(self.temp)
            self.umidade_lida = int(self.umid)

            self.temperatura_indicada = ((145 * self.temperatura_lida) + 7250 - (-40500)) / 150
            
            if self.temperatura_lida > 100.0 : self.temperatura_lida = -50.0
            if self.temperatura_lida <= 10.0:
                self.cor_indicador_t = [0.51,0.7,0.82,1]
            elif 10.0 < self.temperatura_lida <= 19.0:
                self.cor_indicador_t = [0.38,0.7,0.9,1]
            elif 19.0 < self.temperatura_lida <= 26.0:
                self.cor_indicador_t = [0.89,0.79,0.33,1]
            elif 26.0 < self.temperatura_lida <= 32.0:
                self.cor_indicador_t = [0.89,0.69,0.33,1]
            elif 32.0 < self.temperatura_lida <= 42.0:
                self.cor_indicador_t = [0.89,0.6,0.33,1]
            elif 42.0 < self.temperatura_lida <= 55.0:
                self.cor_indicador_t = [0.93,0.37,0.33,1]
            elif 55.0 < self.temperatura_lida <= 100.0:
                self.cor_indicador_t = [1,0,0,1]

            self.umidade_indicada = ((145 * self.umidade_lida) + 0 - (-27000)) / 100
            
            if self.umidade_lida <= 10.0:
                self.cor_indicador_u = [1,0,0,1]
            elif 10.0 < self.umidade_lida <= 30.0:
                self.cor_indicador_u = [0.5,0.5,0,1]
            elif 30.0 < self.umidade_lida <= 50.0:
                self.cor_indicador_u = [0,0.5,0,1]
            elif 50.0 < self.umidade_lida <= 70.0:
                self.cor_indicador_u = [0,1,0,1]
            elif 70.0 < self.umidade_lida <= 100.0:
                self.cor_indicador_u = [0,0,1,1]
        except:
            pass

    @mainthread
    def le_temp_umid(self):
        if self.teste_serial:
            if self.conta_leitura_th >= 200:
                self.conta_leitura_th = 0
                try:
                    command_line = 'A0TR'
                    write_data = self.ser.write(command_line)
                    self.conta_leitura_th = 0
                    line = self.ser.readline()
                    print line
                    if line != None or line != '':
                        line = line.split(',')
                        if line[0] == 'T':
                            if line[1] == '0':
                                self.alr_st_img = 'imagens/diversos/usb.png'
                                self.msg_sens_th = ''
                                self.cor_fundo_indicador = [0.83,0.90,0.97,1]
                            elif line[1] == '1':
                                self.alr_st_img = 'imagens/diversos/usb_vm.png'
                                self.msg_sens_th = 'FALHA SENSORES TEMPERATURA/UMIDADE'
                                self.cor_fundo_indicador = [1,0,0,1]
                            elif line[1] == '2':
                                self.alr_st_img = 'imagens/diversos/usb_vm.png'
                                self.msg_sens_th = 'FALHA SENSORES TEMPERATURA/UMIDADE'
                                self.cor_fundo_indicador = [1,0,0,1]
                            elif line[1] == '3':
                                self.alr_st_img = 'imagens/diversos/usb_vm.png'
                                self.msg_sens_th = 'FALHA EMINENTE SENSORES TEMPERATURA/UMIDADE'
                                self.cor_fundo_indicador = [1,1,0,1]
                            elif (line[1] == '4') or (line[1] == '5') or (line[1] == '6'):
                                self.alr_st_img = 'imagens/diversos/usb_vm.png'
                                self.msg_sens_th = 'FALHA SENSORES TEMPERATURA/UMIDADE'
                                self.cor_fundo_indicador = [1,0,0,1]
                            self.temp = line[2]
                            self.umid = line[3]
                    else:
                        self.alr_st_img = 'imagens/diversos/usb_vm.png'
                        print "Falha de leitura"
                except Exception, e:
                    print e
                    self.teste_serial = False
                    self.alr_st_img = 'imagens/diversos/usb_vm.png'
                    self.temp = 0
                    self.umid = 0
            else:
                self.conta_leitura_th += 1
        else:
            self.temp = 0
            self.umid = 0


    def init_system(self):
        st_sys = JsonStore('json/status.json')
        try:
            self.temperatura_indicada = ((145 * 0) + 7250 - (-40500)) / 150
            
            if self.temperatura_lida > 100.0 : self.temperatura_lida = -50.0
            if self.temperatura_lida <= 10.0:
                self.cor_indicador_t = [0.51,0.7,0.82,1]
            elif 10.0 < self.temperatura_lida <= 19.0:
                self.cor_indicador_t = [0.38,0.7,0.9,1]
            elif 19.0 < self.temperatura_lida <= 26.0:
                self.cor_indicador_t = [0.89,0.79,0.33,1]
            elif 26.0 < self.temperatura_lida <= 32.0:
                self.cor_indicador_t = [0.89,0.69,0.33,1]
            elif 32.0 < self.temperatura_lida <= 42.0:
                self.cor_indicador_t = [0.89,0.6,0.33,1]
            elif 42.0 < self.temperatura_lida <= 55.0:
                self.cor_indicador_t = [0.93,0.37,0.33,1]
            elif 55.0 < self.temperatura_lida <= 100.0:
                self.cor_indicador_t = [1,0,0,1]

            self.umidade_indicada = ((145 * 0) + 0 - (-27000)) / 100
            
            if self.umidade_lida <= 10.0:
                self.cor_indicador_u = [1,0,0,1]
            elif 10.0 < self.umidade_lida <= 30.0:
                self.cor_indicador_u = [0.5,0.5,0,1]
            elif 30.0 < self.umidade_lida <= 50.0:
                self.cor_indicador_u = [0,0.5,0,1]
            elif 50.0 < self.umidade_lida <= 70.0:
                self.cor_indicador_u = [0,1,0,1]
            elif 70.0 < self.umidade_lida <= 100.0:
                self.cor_indicador_u = [0,0,1,1]

            #st_sys.put('alrm', st=1)
        except:
            pass

# #############################################################################


class Sm(ScreenManager):
    # Gerenciamento de páginas
    sm = ScreenManager()

    def switch_to(self, screen, outros_comandos='', **options):
        self.current = screen

	def switch_to_paginahome(self):
    		self.current = 'home'


# ###########################################################################

class Util(object):
    pass

# ###########################################################################

class ctrlhome(App):

    def on_pause(self):
        return True



    def on_start(self):
        pass


    def on_stop(self):
        pass


    def on_resume(self):
        pass

    def build(self):
        self.root = Sm(transition=NoTransition())
        self.title = 'HomeFacil - IoT System - ARGOS - Tenologia & Sistemas'
        return self.root


if __name__ == '__main__':
    ctrlhome().run()
