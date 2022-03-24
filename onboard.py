from jinja2 import Environment, FileSystemLoader 
from f5sdk.bigip import ManagementClient
from f5sdk.bigip.extension import DOClient
import time

class OnboardSuite:
    
    def __init__(self, do_target_ip, do_template, do_data, pw, update):
        self.do_target_ip = do_target_ip
        self.do_template = do_template
        self.pw = pw
        self.do_data = do_data
        if update:
            self.do_version = update
        else:
            self.do_version = '1.27.1-2'
    
    def RenderDeclaration(self):
        '''Load jinja2 declaration template and render it with vars taken
        from CLI'''
        dir = '.'
        env = Environment(loader=FileSystemLoader(dir))
        template = env.get_template(self.do_template)
        self.template_content = template.render(self.do_data)

    def WriteDeclarationFile(self):
        '''Write the declaration to a file so that it can be used by 
        the DO module'''
        self.declaration = open('declaration_' + self.do_target_ip 
            + '.json', 'w+')
        self.declaration.write(self.template_content)
        self.declaration.close()
                
    def Connect2Service(self):
        # Create device and DO clients from f5sdk package
        self.device = ManagementClient(self.do_target_ip, user='admin', 
            password=self.pw)
        self.do = DOClient(self.device)

    def InstallDOPackage(self):
        # Install DO RPM then add a short delay for SW to initialize
        self.package_url = 'https://github.com/F5Networks/'\
            + 'f5-declarative-onboarding/'\
            + 'releases/download/v' + self.do_version.split('-')[0]\
            + '/f5-declarative-onboarding-' + self.do_version \
            + '.noarch.rpm'
        if not self.do.package.is_installed()['installed']:
            self.do.package.install(package_url=self.package_url)
            # Wait for installation to complete
            time.sleep(15)

    def CreateService(self):
        '''Use the DO client to deploy declaration then store result from
        returned dict'''
        self.create = self.do.service.create(config_file='declaration_' 
            + self.do_target_ip + '.json')

class OnboardDSC(OnboardSuite):

    def __init__(self, do_target_ip, do_template, do_data, pw, update):
        # Initialize vars from parent
        OnboardSuite.__init__(self, do_target_ip, do_template, do_data,
                pw, update)

    def RunAllOnboard(self):
        # Run all functions from parent to simplify execution
        OnboardSuite.RenderDeclaration(self)
        OnboardSuite.WriteDeclarationFile(self)
        OnboardSuite.Connect2Service(self)
        OnboardSuite.InstallDOPackage(self)
        OnboardSuite.CreateService(self)
