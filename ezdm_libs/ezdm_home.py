from frontend import Session, Page


class HOME(Session):
    def render(self, requestdata):
        page = Page()
        if requestdata:
            self.destroy()
        page.add('COPYING.tpl', {})
        return page.render()
