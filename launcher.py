import sys
import os
title = r"""
                                             $$\                         
                                             $$ |                        
 $$$$$$$\  $$$$$$\  $$$$$$\$$$$\   $$$$$$\ $$$$$$\    $$$$$$\   $$$$$$$\ 
$$  _____|$$  __$$\ $$  _$$  _$$\ $$  __$$\\_$$  _|  $$  __$$\ $$  _____|
$$ /      $$ /  $$ |$$ / $$ / $$ |$$ /  $$ | $$ |    $$$$$$$$ |\$$$$$$\  
$$ |      $$ |  $$ |$$ | $$ | $$ |$$ |  $$ | $$ |$$\ $$   ____| \____$$\ 
\$$$$$$$\ \$$$$$$  |$$ | $$ | $$ |$$$$$$$  | \$$$$  |\$$$$$$$\ $$$$$$$  |
 \_______| \______/ \__| \__| \__|$$  ____/   \____/  \_______|\_______/ 
                                  $$ |                                   
                                  $$ |                                   
                                  \__|
"""

print('Python --->', sys.version)
print(title)

__folder__ = os.path.dirname(__file__)
source_folder = os.path.join(__folder__, 'source')

if source_folder not in sys.path:
    sys.path.append(source_folder)


from comptes.ui import open_comptes
open_comptes()