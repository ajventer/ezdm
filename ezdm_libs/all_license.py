from frontend import Session, Page


class LICENSE(Session):
    def render(self, requestdata):
        page = Page()
        if requestdata:
            self.destroy()
        page.message(page.tplrender('COPYING.tpl', {}))
        return page.render()
