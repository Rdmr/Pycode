import os
import wx
import wx.lib.agw.aui as aui
from PySTC import PySTC as PyTextCtrl
import wx.lib.agw.flatnotebook as fnb
import pymite
import settings


class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title = title, size = settings.WIN_SIZE)
        #Init notebook
        self.notebook = fnb.FlatNotebook(self, wx.ID_ANY, agwStyle = fnb.FNB_MOUSE_MIDDLE_CLOSES_TABS | fnb.FNB_NO_TAB_FOCUS | fnb.FNB_X_ON_TAB | fnb.FNB_SMART_TABS | fnb.FNB_DROPDOWN_TABS_LIST | fnb.FNB_FF2)
        self.textControls = []
        self.NewTab()
        #self.textControls[-1].SetFocus()
       
        self.CreateRightClickOnTabMenu()
        self.notebook.SetRightClickMenu(self._rmenu)
        
        #Init docking windows
        self.CreateWindows()
        self.CreateMenuBar()
        self.CreateCustomToolbar()
        self.CreateStatusBar() # A StatusBar in the bottom of the window        

        self.notebook.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CONTEXT_MENU, self.OnNotebookContextMenu)
        self.notebook.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSED, self.OnCloseTab)
        self.notebook.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)

        self.Centre()
        self.Show(True)

    def OnDummy(self, event):
        pass
        
    def CreateWindows(self):
        #TODO: fix bug with hidden info/output tabs
        self.infoText = wx.TextCtrl(self, wx.ID_ANY, '',
                            wx.DefaultPosition, wx.Size(*settings.INFOWIN_SIZE),
                            wx.NO_BORDER | wx.TE_MULTILINE | wx.TE_READONLY)
        
        self.outputText = wx.TextCtrl(self, wx.ID_ANY, '',
                            wx.DefaultPosition, wx.Size(*settings.OPTWIN_SIZE),
                            wx.NO_BORDER | wx.TE_MULTILINE | wx.TE_READONLY)
                            
        self.WinManager = aui.AuiManager(self)
        self.WinManager.AddPane(self.notebook, wx.CENTER)
        self.WinManager.AddPane(self.outputText, wx.BOTTOM, 'Output')
        self.WinManager.AddPane(self.infoText, wx.BOTTOM, 'Information', target = self.WinManager.GetPane(self.outputText))
        self.WinManager.GetPane(self.infoText).Caption('Information')
        self.WinManager.Update()
    
    def CreateCustomToolbar(self):
        toolbarData = (("New", "data/new.png", "Create new sketch",  self.OnNewTab),
                        ("Open", "data/open.png", "Open existing sketch", self.OnOpen),
                        ("Save", "data/save.png", "Save existing sketch", self.OnSave),
                        ("Save as", "data/save_as.png", "Save existing sketch as", self.OnSaveAs),
                        ("", "", "", ""),
                        ("", "", "", ""),
                        ("Run", "data/run.png", "Load and run", self.OnLoadAndRun),
                        ("Pymite", "data/pymite.png", "Compile and load Pymite", self.OnDummy),          
                      )
    
        toolbar = self.CreateToolBar()
        for to_help, to_img, to_lhelp, to_handle in toolbarData:
            if to_help:
                tool = toolbar.AddLabelTool(wx.NewId(), '', wx.Bitmap(to_img), shortHelp=to_help, longHelp=to_lhelp)
                self.Bind(wx.EVT_MENU, to_handle, tool)
            else:
                toolbar.AddSeparator()       
        toolbar.Realize()

    def CreateMenuBar(self):
        menuData = (("&File",
                     ("&New", "Create new sketch", self.OnNewTab),   
                     ("&Open", "Open existing sketch", self.OnOpen),
                     ("&Save", "Save existing sketch", self.OnOpen),
                     ("&Save as", "Save existing sketch as", self.OnOpen),
                     ("&Quit", "Quit", self.OnExit)),
                    ("&Edit",
                     ("&Copy", "Copy", self.OnDummy),
                     ("C&ut", "Cut", self.OnDummy),
                     ("&Paste", "Paste", self.OnDummy),
                     ("", "", ""),
                     ("&Options...", "DisplayOptions", self.OnDummy)),
                    ("&Program",
                     ("&Compile program", "Compile Python code", self.OnDummy),
                     ("C&ompile and run", "Compile and run code on the device", self.OnLoadAndRun),
                     ("Co&mpile Pymite ", "Compile Pymite and write to the flash ", self.OnCompilePyMite)),
                    ("&Help",
                     ("&About", "About", self.OnAbout),
                     ))
    
        menuBar = wx.MenuBar()                                                                
        for eachMenuData in menuData:
              menuLabel = eachMenuData[0]
              menuItems = eachMenuData[1:]
              menuBar.Append(self.createMenu(menuItems), menuLabel)
        self.SetMenuBar(menuBar)
        
    def createMenu(self, menuData):
        menu = wx.Menu()
        for menuLabel, menuStatus, menuHandler in menuData:
              if menuLabel:
                  menuItem = menu.Append(-1, menuLabel, menuStatus)
                  self.Bind(wx.EVT_MENU, menuHandler, menuItem)
              else:
                  menu.AppendSeparator()              
        return menu

    def OnKeyDown(self, event):
        key = event.GetKeyCode()
        if (key == 'n' or key == 'N') and event.ControlDown(): #FIXME: it works only in English keyboard layout
            self.OnNewTab([])

    def OnNotebookContextMenu(self, e):
        self.notebook.SetSelection(e.GetSelection())

    def CreateRightClickOnTabMenu(self):
        self._rmenu = wx.Menu()
        item = wx.MenuItem(self._rmenu, wx.ID_ANY,
                           "Close Tab\tCtrl+F4",
                           "Close Tab")
        self.Bind(wx.EVT_MENU, self.onDeletePage, item)
        self._rmenu.AppendItem(item)
        
    def onDeletePage(self, event):
        """
        Removes a page from the notebook
        """
        self.notebook.DeletePage(self.notebook.GetSelection())

    def OnAbout(self,e):
        # A message dialog box with an OK button. wx.OK is a standard ID in wxWidgets.
        dlg = wx.MessageDialog( self, "A small Python-code editor", "About Pycode Editor", wx.OK)
        dlg.ShowModal() # Show it
        dlg.Destroy() # finally destroy it when finished.

    def OnExit(self,e):
        self.Close(True)  # Close the frame.
        
    def OnCompilePyMite(self, e):
        text = pymite.Compile()
        self.infoText.SetValue(text)

        #text = pymite.LoadDfu()
        #self.infoText.AppendText(text)
        #self.infoText.SetValue(text)
        pass    
        
    def OnLoadAndRun(self, e):
        src = self.notebook.GetCurrentPage().GetText()
        text = pymite.loadtoipm(src, PORT = settings.PORT, BAUD = settings.BAUD)
        self.outputText.SetValue(text)
        pass    
        
    def OnSave(self, e):
        """ Save a file"""
        page, fullfilename = self.textControls[self.notebook.GetSelection()]
        if fullfilename:
            open(fullfilename, 'w').write(self.notebook.GetCurrentPage().GetText())
        else:
            self.OnSaveAs(e)
        
    def OnSaveAs(self, e):
        """ Save a file"""
        #result = False
        dlg = wx.FileDialog(self, "Choose a file", "", "", "*.py", wx.SAVE  | wx.OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            fullfilename = os.path.join(dlg.GetDirectory(), dlg.GetFilename())
            open(fullfilename, 'w').write(self.notebook.GetCurrentPage().GetText())
            #result = True
            self.notebook.SetPageText(self.notebook.GetSelection(), dlg.GetFilename())
            page, tmp = self.textControls[(e.GetSelection())]
            self.textControls[(e.GetSelection())] = page, fullfilename
        dlg.Destroy()
        #return result

        
    def NewTab(self, title = "Untitled", fullfilename = None):
        tab = PyTextCtrl(self.notebook, self)
        self.textControls.append((tab, fullfilename))
        self.notebook.AddPage(tab, title)
        self.notebook.SetSelection(len(self.textControls)-1)    
        
    def OnOpen(self, e):
        """ Open a file"""
        dlg = wx.FileDialog(self, "Choose a file", "", "", "*.py", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetFilename()
            dirname = dlg.GetDirectory()
            fullfilename = os.path.join(dirname, filename)
            self.NewTab(filename)
            f = open(fullfilename, 'r')
            self.notebook.GetCurrentPage().SetText(f.read())
            f.close()
        dlg.Destroy()
        
    def OnNewTab(self, e):
        self.NewTab()
        
    def OnCloseTab(self, e):
        self.textControls.pop(e.GetSelection())

app = wx.App(False)
frame = MainWindow(None, "Pycode editor")
app.MainLoop()
