$i++;
$cfg['Servers'][$i]['verbose'] = 'Remote server 3306';
$cfg['Servers'][$i]['host'] = 'remoteserver';
$cfg['Servers'][$i]['port'] = '3306';
$cfg['Servers'][$i]['connect_type'] = 'tcp';
$cfg['Servers'][$i]['extension'] = 'mysqli';
$cfg['Servers'][$i]['auth_type'] = 'cookie';
$cfg['Servers'][$i]['AllowNoPassword'] = false;