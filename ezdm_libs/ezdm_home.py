from frontend import Session


class HOME(Session):
    def render(self, requestdata):
        if requestdata:
            self.destroy()
        self.page.add('COPYING.tpl', {})
        return self.page.render()
