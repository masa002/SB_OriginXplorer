import wx
from scipy.optimize import least_squares
import numpy as np

# station positions
stations = {i: np.array([0, 0, 0]) for i in range(1, 31)}
stations.update({
    1: np.array([-1.514, -58.557, 14.605]), 2: np.array([-12.356, -53.133, 9.482]), 3: np.array([-30.412, -39.176, 4.620]),
    4: np.array([-30.412, -39.176, 4.620]), 5: np.array([-35.894, -28.937, -0.569]), 6: np.array([-40.449, -19.201, -5.273]),
    7: np.array([-45.639, -9.224, -5.593]), 8: np.array([-45.676, 0.511, -5.543]), 9: np.array([-45.810, 10.676, -5.501]),
    10: np.array([-41.736, 22.001, -5.152]), 11: np.array([-37.458, 30.822, -0.743]), 12: np.array([-32.408, 40.743, 4.281]),
    13: np.array([-22.508, 50.948, 9.390]), 14: np.array([-12.627, 56.072, 9.548]), 15: np.array([-2.299, 61.232, 14.458]),
    16: np.array([7.554, 61.302, 14.522]), 17: np.array([17.836, 56.855, 10.092]), 18: np.array([28.872, 51.332, 9.665]),
    19: np.array([38.334, 42.004, 4.963]), 20: np.array([43.363, 32.331, 0.081]), 21: np.array([48.612, 22.216, -5.050]),
    22: np.array([53.755, 11.921, -5.458]), 23: np.array([53.982, 1.680, -5.390]), 24: np.array([53.948, -8.049, -5.410]),
    25: np.array([48.380, -18.037, -5.330]), 26: np.array([44.005, -28.331, -0.466]), 27: np.array([38.773, -38.244, 4.672]),
    28: np.array([28.909, -48.311, 9.594]), 29: np.array([18.452, -53.450, 9.642]), 30: np.array([8.356, -58.735, 15.266]),
})


class Mywin(wx.Frame):
    def __init__(self, parent, title) -> None:
        super(Mywin, self).__init__(parent, title = title, size = (250,280), style=wx.DEFAULT_FRAME_STYLE & ~wx.MAXIMIZE_BOX ^ wx.RESIZE_BORDER | wx.STAY_ON_TOP)
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.combos = {}
        self.distances = {}
        for i in [8, 15, 23, 30]:
            box = wx.BoxSizer(wx.HORIZONTAL)
            self.distances[i] = wx.SpinCtrl(panel, -1, '', min=0, max=1000000)

            box.Add(wx.StaticText(panel, -1, "Origin"), 1, flag = wx.EXPAND|wx.ALIGN_LEFT|wx.ALL, border = 5)
            self.combos[i] = wx.ComboBox(panel, choices=[str(i) for i in range(1, 31)], value=str(i))
            box.Add(self.combos[i], 1, flag = wx.EXPAND|wx.ALIGN_LEFT|wx.ALL, border = 5)
            box.Add(wx.StaticText(panel, -1, "Distance"), 1, flag = wx.EXPAND|wx.ALIGN_LEFT|wx.ALL, border = 5)
            box.Add(self.distances[i], 1, flag = wx.EXPAND|wx.ALIGN_LEFT|wx.ALL, border = 5)
            vbox.Add(box, 1, flag = wx.EXPAND|wx.ALIGN_LEFT|wx.ALL, border = 5)

        box2 = wx.BoxSizer(wx.HORIZONTAL)
        # copy to clipboard checkbox
        # default checked
        self.cb = wx.CheckBox(panel, -1, 'Copy to clipboard')
        self.cb.SetValue(True)
        box2.Add(self.cb, 1, flag = wx.ALIGN_CENTER)

        self.btn = wx.Button(panel, -1, "Calculate", size = (100,30))
        box2.Add(self.btn, 1, flag = wx.ALIGN_CENTER)
        self.Bind(wx.EVT_BUTTON, self.OnClicked, self.btn)
        vbox.Add(box2, 1, flag = wx.EXPAND|wx.ALIGN_LEFT|wx.ALL, border = 5)

        # signature
        self.sig = wx.StaticText(panel, -1, "OriginXplorer v1.0 / Create by Masakk")
        vbox.Add(self.sig, 1, flag = wx.ALIGN_CENTER|wx.ALL, border = 5)
        panel.SetSizer(vbox)
        self.Centre()
        self.Show(True)

    def OnClicked(self, event) -> None:
        origins = [int(self.combos[i].GetValue()) for i in [8, 15, 23, 30]]
        if len(set(origins)) != 4:
            dlg = wx.MessageDialog(self, "Each origin must be unique.", "Error", wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
            return

        distances = [float(self.distances[i].GetValue()) for i in [8, 15, 23, 30]]
        result = self.calculate_current_position(origins, distances)

        # round with int
        result = np.round(result*1000).astype(int)

        if self.cb.GetValue():
            wx.TheClipboard.Open()
            wx.TheClipboard.SetData(wx.TextDataObject(' '.join([str(int(i)) for i in result])))
            wx.TheClipboard.Close()

        # attach labels X, Y, Z
        result = dict(zip(['X', 'Y', 'Z'], result))
        result = ', '.join(['{}: {}'.format(k, v) for k, v in result.items()])

        dlg = wx.MessageDialog(self, str(result), "Current Position", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def calculate_current_position(self, origins, distances) -> np.ndarray:
        def fun(x):
            return [np.linalg.norm(x - stations[i]) - d for i, d in zip(origins, distances)]

        res = least_squares(fun, np.zeros(3))
        return res.x

app = wx.App()
Mywin(None,"OriginXplorer")
app.MainLoop()
