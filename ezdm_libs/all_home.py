from frontend import Session, Page
import frontend


class HOME(Session):
    def render(self, requestdata):
        page = Page()
        if requestdata:
            self.destroy()
        if frontend.mode == 'dm':
        	page.add('COPYING.tpl', {})
        
        return page.render()
