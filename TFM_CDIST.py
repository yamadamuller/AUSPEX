#Otimização do algoritmo original TFM_MateusYM

import matplotlib.pyplot as plt
import numpy as np
import scipy
from scipy.spatial.distance import cdist
from scipy.signal import hilbert

file = 'D:\Documentos\AUSPEX\IMPLEMENTAÇÕES\TFM\TFM\dados_tfm.npy'

dados = np.load(file, allow_pickle=True).item()
ascans = dados.get('ascans')
speed_m_s = dados.get('speed_m_s')
f_sampling_MHz = dados.get('f_sampling_MHz')
samples_t_init_microsec = dados.get('samples_t_init_microsec')
elem_positions_mm = dados.get('elem_positions_mm')

#renomeando as variáveis
cl = speed_m_s #velocidade
f = f_sampling_MHz #frequência
t_init = samples_t_init_microsec #tempo
x = elem_positions_mm #posições transdutor

#variáveis de análise
t = np.zeros((1858,1))
for linha in range(1858):
    t_i = (t_init + linha/f) #tempo das 1858 amostras em microsegundos
    t[linha] += t_i

z=(cl*t/2)*1e-3 #posições no eixo z em mm

#ascans relativos a região de interesse
g = ascans[:, :, :]

#ROI do ensaio
referencia = np.zeros((1, 2))  # [i,j] = [0,0]
inicio = referencia + [-18.9,z[0]]
h = z[1012]  # altura da ROI
h_z = 1013  # numero de pontos em z
l = 37.8  # largura da ROI
l_z = 64  # numero de pontos em x

# Eixo z
# retorna os pontos de z igualmente espaçados
h_pontos = np.linspace(z[0], h, num=int(h_z), endpoint=True)
altura = h_pontos[-1] + h_pontos[1] - 2 * h_pontos[0] #Altura da ROI

# Eixo x
# retorna os pontos de x igualmente espaçados
l_pontos = np.linspace(inicio[0, 0], inicio[0,0]+l, num=int(l_z), endpoint=True)
largura = l  # Largura da ROI
#Coordenadas da ROI
ROI = np.array(np.meshgrid(l_pontos, h_pontos, indexing='ij')).reshape((2, -1)).T
#print('ROI = {}' .format(ROI))
#Coordenadas do transdutor
coord_transd = np.array(np.meshgrid(l_pontos, 0, indexing='ij')).reshape((2,-1)).T
#print('coord_transd = {}' .format(coord_transd))

#Distâncias
dist = cdist(coord_transd,ROI) #distancia entre todos os centros dos transdutores e a ROI
#print(dist.shape)
dist_form = dist.reshape(64,64,1013)
dist_final = np.transpose(dist_form,(1,-1,0))
#print(dist_final)
#print(dist_final.shape)
#print(dist_final)
#print(dist_final[0].shape)

def tfm (dist_final,cl,t,g):
    f = np.zeros((1013,64))
    for emissor in range(64):
        for receptor in range(64):
            for linha in range(1013):
                for coluna in range(64):
                    dist_calc = dist_final[emissor,linha,coluna] + dist_final[receptor,linha,coluna]
                    t_e_r = (dist_calc/cl)*1e3
                    indice = np.argmin(np.abs(t - t_e_r))
                    f[linha,coluna] += g[indice,emissor,receptor]

    for coluna in range(64):
        f[:, coluna] = np.abs(scipy.signal.hilbert(f[:, coluna])) #pós processamento, calcula a envoltória pela transformada de hilbert
    f = np.abs(f)
    print('final = {}' .format(f))
    return f

plt.figure()
f = tfm(dist_final,cl,t,g)
plt.imshow(f, aspect="auto")
plt.title('TFM')
plt.show()
