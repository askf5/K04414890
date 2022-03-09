from jinja2 import Environment, FileSystemLoader 
from f5sdk.bigip import ManagementClient
from f5sdk.bigip.extension import DOClient
import time

class OnboardSuite:
    
    def __init__(self, do_target_ip, mgmt_ip_1, mgmt_ip_2, int_self_ip, 
        ext_self_ip, pw):
        self.do_target_ip = do_target_ip
        self.mgmt_ip_1 = mgmt_ip_1
        self.mgmt_ip_2 = mgmt_ip_2
        self.int_self_ip = int_self_ip
        self.ext_self_ip = ext_self_ip
        self.pw = pw
    
    def RenderDeclaration(self):
        '''Load jinja2 declaration template and render it with vars taken
        from CLI'''
        dir = '.'
        json_template = 'DSC_VLAN_template.json'
        env = Environment(loader=FileSystemLoader(dir))
        template = env.get_template(json_template)
        self.template_content = template.render(
            mgmt_ip=self.do_target_ip,
            mgmt_ip_1=self.mgmt_ip_1, 
            mgmt_ip_2=self.mgmt_ip_2,
            int_self_ip=self.int_self_ip,
            ext_self_ip=self.ext_self_ip
        )

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
            + 'releases/download/v1.27.0/'\
            + 'f5-declarative-onboarding-1.27.0-6.noarch.rpm'
        if not self.do.package.is_installed()['installed']:
            self.do.package.install(package_url=self.package_url)
            # Wait for installation to complete
            time.sleep(15)

    def CreateService(self):
        '''Use the DO client to deploy declaration then store result from
        returned dict'''
        self.create = self.do.service.create(config_file='declaration_' 
            + self.do_target_ip + '.json')

    def ValidateService(self):
        '''Validate configuration was successfully deployed from actual values
        returned by devices'''
        self.dsc_ip = self.device.make_request('/mgmt/tm/cm/device/'
            + '?$select=configsyncIp,unicastAddress')
        self.device_group = self.device.make_request('/mgmt/tm/cm/device-group/'
            + '~Common~failoverGroup/devices/')
        self.device_trust = self.device.make_request('/mgmt/tm/cm/trust-domain/'
            + '~Common~Root/?$select=caDevices')
        self.vlans =  self.device.make_request('/mgmt/tm/net/vlan/'
            + '?expandSubcollections=true&$select=name,tag,'
            + 'interfacesReference/items/name,'
            + 'interfacesReference/items/untagged')
        self.selfips = self.device.make_request('/mgmt/tm/net/self/'
            + '?$select=address,vlan')

class OnboardDSC(OnboardSuite):

    def __init__(self, do_target_ip, mgmt_ip_1, mgmt_ip_2, int_self_ip, 
        ext_self_ip, pw):
        # Initialize vars from parent
        OnboardSuite.__init__(self, do_target_ip, mgmt_ip_1, mgmt_ip_2, 
            int_self_ip, ext_self_ip, pw)

    def RunAllOnboard(self):
        # Run all functions from parent to simplify execution
        OnboardSuite.RenderDeclaration(self)
        OnboardSuite.WriteDeclarationFile(self)
        OnboardSuite.Connect2Service(self)
        OnboardSuite.InstallDOPackage(self)
        OnboardSuite.CreateService(self)
        OnboardSuite.ValidateService(self)
