import sublime, sublime_plugin, re
import urllib.request
import json
import os
import tempfile

import subprocess
import threading

""" 
	api de referencia

	http://www.sublimetext.com/docs/2/api_reference.html#sublime.View

"""


class  SqlblimeCommand(sublime_plugin.TextCommand):

	variaveis   = []
	var_temp    = []
	query       = ""
	query_final = ""
	edit        = None
	configs 	= None

	def run(self, edit):		

		self.configs = self.loadConfigs()
		# buscando na configuracao
		print(self.configs.get('banco'))
		temSelecao = self.get_selecao()

		# self.nova_aba(self,"novo")
		self.showPainel( temSelecao )

		# if temSelecao != "":
		# 	self.variaveis = self.get_php_var(temSelecao)		
		# 	self.query = temSelecao
		# 	print( self.query)

		# 	# sublime.message_dialog("User said: " );
		# 	# dialogo para coletar dados
		# 	# self.dialog_var(self.dialog_var(self.variaveis[0]))

		# 	cont=0

		# 	while cont < 2:				

		# 		# self.dialog_var( self.variaveis[0] )
		# 		# print( self.variaveis[ cont-1 ] )				
				
		# 		cont += 1

		# 	# self.replace_query( self.query )
		# 	print( self.variaveis )

	"""	
		funcao que busca e analisa 
		a string para verificar se ela contem 
		uma query """
	def get_selecao(self):

		sels = self.view.sel()
		# percorrendo os pontos 
		for sel in sels:
			if self.is_SQL( self.view.substr(sel) ):
				return self.view.substr(sel)
				
		return False

	def is_SQL(self, sql):
		dado = re.compile(r'SELECT+', re.IGNORECASE)
		
		if( dado.search( sql ) ):
			return True
		return False		

	def get_JSON(self, query, edit ):		
		# setando as variaveis achada na query
		url = "http://192.168.0.50/projetos/jordan/teste.php"		
		values = {'acao' : 'query', 'sql': query }
		
		data = urllib.parse.urlencode(values)
		data = data.encode('utf-8')
		
		req = urllib.request.Request(url, data)
		resp = urllib.request.urlopen(req)		
		respData = resp.read().decode(resp.info().get_param('charset') or 'utf-8')

		self.carrega_conteudo_JSON(respData,edit )				
	
	def get_php_var(self, query ):

		lista_ini 	  = []		
		lista_fim 	  = []
		php_variaveis = []	

		indice = 0		
		while indice < len(query):    			
    		
			if query[indice] == '{':
				lista_ini.append( indice+1 )

			if query[indice] == '}':
				lista_fim.append( indice )
    		
			indice = indice + 1		

		cont = 0
		while cont < len(lista_ini):
			php_variaveis.append( query[lista_ini[cont]:lista_fim[cont] ] )
			cont+=1

		return php_variaveis	

	def carrega_conteudo_JSON(self, dados, edit):
		print("comecando")	
		
		dados_json = json.loads(dados)

		coluna = dados_json.keys()
		# i=0
		# while ( i < 5 ):

		# 	for dado in dados_json[ i ]:			
		# 		coluna +=  dado + "\t" 

		# 	i = i + 1

		coluna += "\n"		

		self.nova_aba( edit, coluna )

	def nova_aba(self, edit, stringDados ):

		janela = self.view.window().new_file()
		janela.insert(edit, 0, stringDados )
		janela.set_name("Consulta")
		janela.set_encoding('utf-8')
		janela.window.set_layout({
    		"cols": [0, 0.5, 1],
    		"rows": [0, 1],
    		"cells": [[0, 0, 1, 1], [1, 0, 2, 1]]
		})
		self.window.active_view(janela)
	
	def on_retorno(self, user_input ):

		# this is displayed in status bar at bottom
		# this is a dialog box, with same message
		# sublime.message_dialog("User said: " + user_input )		
		self.var_temp.append( user_input )
		
		
		# sublime.status_message( user_input )

	def replace_query(self, query):

		nova_query = ""
		cont = 0
		while cont < len(self.variaveis):
			nova_query = query.replace( self.variaveis[cont], self.var_temp[cont]  )					
			cont += 1

		nova_query = nova_query.replace('}',"")
		nova_query = nova_query.replace('{',"")		
		self.query_final = nova_query; 

	def dialog_var(self, termo):
		self.view.window().show_input_panel("Valor temporario para as Variaveis "+ termo + "=", "", self.on_retorno, None, None) 

	def msg_error(self, mensagem):	
		sublime.error_message("Must be and error!")

	def showPainel( self, dados ):
		self.window = self.view.window()
		output = self.window.create_output_panel("consulta")
		
		output.run_command('erase_view')
		output.run_command('append', {'characters': dados})
		output.set_syntax_file("Packages/SQL/SQL.tmLanguage")

		self.window.run_command("show_panel", {"panel": "output.consulta"})		

	def loadConfigs( self ):
		return sublime.load_settings('sqlblime.sublime-settings')

	def textoSelecionado(selections):
		"""Retorna true se tiver algum texto selecionado"""
		for selection in selections:
			if selection.a != selection.b:
				return True
			return False
	def chamaProcesso(self, processo = 'notepad.exe'):
		subprocess.call(processo)



