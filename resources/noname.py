# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Jun 30 2011)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class SubiTGuiMain
###########################################################################

class SubiTGuiMain ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"SubiT", pos = wx.DefaultPosition, size = wx.Size( 710,400 ), style = wx.DEFAULT_FRAME_STYLE, name = u"SubiT" )
		
		self.SetSizeHintsSz( wx.Size( 710,400 ), wx.Size( 710,400 ) )
		self.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_MENU ) )
		self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_MENU ) )
		
		MainGrip = wx.FlexGridSizer( 2, 1, 0, 0 )
		MainGrip.SetFlexibleDirection( wx.BOTH )
		MainGrip.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		MainGrip.SetMinSize( wx.Size( 710,390 ) ) 
		UpperGrip = wx.GridSizer( 0, 1, 0, 0 )
		
		UpperGrip.SetMinSize( wx.Size( 710,-1 ) ) 
		LogGrip = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Log" ), wx.VERTICAL )
		
		LogGrip.SetMinSize( wx.Size( 691,131 ) ) 
		self.m_listCtrl1 = wx.ListCtrl( self, wx.ID_ANY, wx.Point( 5,20 ), wx.Size( 681,101 ), 0 )
		self.m_listCtrl1.SetMinSize( wx.Size( 681,101 ) )
		self.m_listCtrl1.SetMaxSize( wx.Size( 681,101 ) )
		
		LogGrip.Add( self.m_listCtrl1, 0, wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		UpperGrip.Add( LogGrip, 1, wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		MainGrip.Add( UpperGrip, 1, wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		LowerGrip = wx.GridSizer( 0, 2, 0, 0 )
		
		LowerGrip.SetMinSize( wx.Size( 710,-1 ) ) 
		LowerLeftGrip = wx.BoxSizer( wx.VERTICAL )
		
		LowerLeftGrip.SetMinSize( wx.Size( 355,-1 ) ) 
		MoviesGrip = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Movies" ), wx.VERTICAL )
		
		MoviesGrip.SetMinSize( wx.Size( 341,-1 ) ) 
		moviesListBoxChoices = []
		self.moviesListBox = wx.ListBox( self, wx.ID_ANY, wx.Point( 5,20 ), wx.Size( 331,101 ), moviesListBoxChoices, 0 )
		self.moviesListBox.SetMinSize( wx.Size( 331,101 ) )
		self.moviesListBox.SetMaxSize( wx.Size( 331,101 ) )
		
		MoviesGrip.Add( self.moviesListBox, 0, wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		InputGrip = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Input" ), wx.VERTICAL )
		
		fgSizer6 = wx.FlexGridSizer( 0, 2, 0, 0 )
		fgSizer6.SetFlexibleDirection( wx.BOTH )
		fgSizer6.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_NONE )
		
		self.inputTextCtrl = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.Point( -1,-1 ), wx.Size( 295,25 ), 0 )
		self.inputTextCtrl.SetMinSize( wx.Size( 295,25 ) )
		self.inputTextCtrl.SetMaxSize( wx.Size( 295,25 ) )
		
		fgSizer6.Add( self.inputTextCtrl, 0, wx.ALL, 5 )
		
		self.browseButton = wx.Button( self, wx.ID_ANY, u"...", wx.Point( -1,-1 ), wx.Size( 30,25 ), wx.BU_EXACTFIT|wx.STATIC_BORDER )
		self.browseButton.SetMinSize( wx.Size( 30,25 ) )
		self.browseButton.SetMaxSize( wx.Size( 30,25 ) )
		
		fgSizer6.Add( self.browseButton, 0, wx.ALL, 5 )
		
		InputGrip.Add( fgSizer6, 1, 0, 1 )
		
		self.m_bpButton3 = wx.BitmapButton( self, wx.ID_ANY, wx.Bitmap( u"icon-go.png", wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, wx.Size( 325,30 ), wx.BU_AUTODRAW )
		self.m_bpButton3.SetMinSize( wx.Size( 325,30 ) )
		self.m_bpButton3.SetMaxSize( wx.Size( 325,30 ) )
		
		InputGrip.Add( self.m_bpButton3, 0, wx.ALL, 5 )
		
		MoviesGrip.Add( InputGrip, 1, 0, 5 )
		
		LowerLeftGrip.Add( MoviesGrip, 1, wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		MenuGrip = wx.FlexGridSizer( 0, 2, 0, 0 )
		MenuGrip.SetFlexibleDirection( wx.BOTH )
		MenuGrip.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_bpButton1 = wx.BitmapButton( self, wx.ID_ANY, wx.Bitmap( u"icon-config.png", wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, wx.Size( -1,-1 ), wx.BU_AUTODRAW )
		MenuGrip.Add( self.m_bpButton1, 0, wx.EXPAND, 5 )
		
		self.m_bpButton2 = wx.BitmapButton( self, wx.ID_ANY, wx.Bitmap( u"icon-about.png", wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, wx.Size( -1,-1 ), wx.BU_AUTODRAW|wx.TRANSPARENT_WINDOW )
		self.m_bpButton2.SetDefault() 
		MenuGrip.Add( self.m_bpButton2, 0, wx.EXPAND, 5 )
		
		LowerLeftGrip.Add( MenuGrip, 1, wx.EXPAND, 5 )
		
		LowerGrip.Add( LowerLeftGrip, 1, 0, 5 )
		
		LowerRightGrip = wx.BoxSizer( wx.VERTICAL )
		
		LowerRightGrip.SetMinSize( wx.Size( 355,-1 ) ) 
		VersionsGrip = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Versions" ), wx.VERTICAL )
		
		VersionsGrip.SetMinSize( wx.Size( 341,-1 ) ) 
		versionsListBoxChoices = []
		self.versionsListBox = wx.ListBox( self, wx.ID_ANY, wx.Point( 5,20 ), wx.Size( 331,221 ), versionsListBoxChoices, 0 )
		self.versionsListBox.SetMinSize( wx.Size( 331,221 ) )
		self.versionsListBox.SetMaxSize( wx.Size( 331,221 ) )
		
		VersionsGrip.Add( self.versionsListBox, 0, 0, 5 )
		
		LowerRightGrip.Add( VersionsGrip, 1, wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		LowerGrip.Add( LowerRightGrip, 1, 0, 5 )
		
		MainGrip.Add( LowerGrip, 1, wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		self.SetSizer( MainGrip )
		self.Layout()
		
		self.Centre( wx.BOTH )
	
	def __del__( self ):
		pass
	

