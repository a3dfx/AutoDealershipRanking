class HtmlTemplate():
    
    def __init__(self):
        self.headerTags = ""
        self.title = ""
        self.body = ""
        self.script = ""
    
    def addHeaders(self, resources):
        for resource in resources:
            if resource[-3:] == ".js":
                startTag = '<script type="text/javascript" src="'
                endTag = "</script>"   
            elif resource[-4:] == ".css":
                startTag = '<link rel="stylesheet" type="text/css" href="'
                endTag = "</link>"  
            self.headerTags += startTag + resource + '" >' + endTag + "\n"
    
    def addBody(self, body):
        self.body = body
        return self
            
    def addScript(self, script):
        self.script = """
            <script>
                %s
            </script>
        """ % script
        return self

    def buildPage(self):
        return """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">        
<html>
    <head>
        <meta http-equiv="X-UA-Compatible" content="IE=9" />
        %(headers)s
        <title>
            %(title)s
        </title>                
    </head>
    <body>       
        %(body)s
        %(script)s
        <script type="text/javascript">
          var _gaq = _gaq || [];
          _gaq.push(['_setAccount', 'UA-33674869-1']);
          _gaq.push(['_trackPageview']);
          (function() {
            var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
            ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
            var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
          })();
        </script>         
    </body>
</html>
        """ % {
           "headers": self.headerTags,
           "title": self.title,
           "body": '<div id="root"></div>' + self.body,
           "script": self.script
        }