
# Removed in support of using pandas
class PrettyMatrix:
    row_titles = None
    col_titles = None
    precision = 3

    def __init__(self, *args, **kwargs):
        self.mat = np.array(*args, **kwargs)

    def _repr_html_(self):
        if self.row_titles is None:
            self.row_titles = [None]*self.shape[0]
        if self.col_titles is None:
            self.col_titles = [None]*self.shape[1]

        html = ["<table>"]
        if self.col_titles[0] is not None:
            html.append("<tr>")
            if self.row_titles[0] is not None:
                html.append("<td></td>")
            for ct in self.col_titles:
                html.append("<td>{}</td>".format(ct))
            html.append("</tr>")

        for (rt, row) in zip(self.row_titles,self.mat):
            html.append("<tr>")
            if rt is not None:
                html.append("<td>"+rt+"</td>")
            for col in row:
                html.append("<td>{:3f}</td>".format(col))
            html.append("</tr>")
        html.append("</table>")
        return ''.join(html)
