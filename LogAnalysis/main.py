import re #Regex: Veri Ayrıştırmak için kullandığım python kütüphanesi.
import subprocess #Powershell komutumu çalıştırmak için kullandığım libary.
from flask import Flask, render_template
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg

veriSayac=0
tarih=[]
adet=[]
uyari=[]
adet2=[]
bugununLogSayisi=""
dununLogSayisi=""
gunsayisi=0
def powerShellFonksiyon():
    # PowerShellden istediğim log düzeni ile loglarımı python projemin bulunduğu dizinde çalıştırılmasını sağladım.
    cmdKomut = "Get-WinEvent -LogName 'System' | Select-Object -Property TimeCreated, Id, LevelDisplayName, Message | Format-Table -AutoSize | Out-File -FilePath .\\Log.txt"
    # PowerShell komutumu çalıştırdım.
    subprocess.run(["powershell.exe", "-Command", cmdKomut])

def tarihAyristirma():
    tarih_deseni = r'\d{2}/\d{2}/\d{4}'  # regex ile tarihleri okumak için bu düzeni kullan dedim.
    # Tarihleri ve sayılarını saklayacak bir sözlük oluşturdum.
    tarih_sozlugu = {}
    # Dosyayı açtım ve içerikleri tek tek okudum ve tarih düzenime göre ayrıştırdım.
    with open("Log.txt", 'r', encoding="utf-16") as dosya:
        global veriSayac
        for satir in dosya:
            tarihler = re.findall(tarih_deseni, satir)
            for tarih in tarihler:
                if tarih in tarih_sozlugu:
                    tarih_sozlugu[tarih] += 1
                    veriSayac =veriSayac+1
                else:
                    tarih_sozlugu[tarih] = 1
                    veriSayac +=1

    with open("TarihAyristirlmis.txt", "w", encoding="utf-16") as dosya2:  # Tarih adlı dosyama ayrıştırdığım verileri yazıyorum
        for tarih, sayi in tarih_sozlugu.items():
            dosya2.write(tarih + " " + str(sayi) + "\n")
            global gunsayisi
            gunsayisi=gunsayisi+1

    # Sonuçları ekrana yazdırın
    for tarih, sayi in tarih_sozlugu.items():
        print(f"{tarih}: {sayi} adet")

    # Dosyayı kapatın
    dosya.close()
def logAyristirma():
    logDeseni = r"(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2})\s+(\d+)\s+(\w+)\s+(.+)"
    #regexin arayacağı log düzeni
    with open("Log.txt", "r", encoding="utf-16") as dosya:
        uyariTip = {}  # UYARI TİPLERİNİ HAFIZADA TUTACAK SÖZLÜK

        uyari=""
        for satir in dosya:
            match = re.match(logDeseni, satir)

            if match:
                tarih,kod, seviye =match.group(0), match.group(2), match.group(3)
                uyari=kod+" "+seviye
            if uyari in uyariTip:
                uyariTip[uyari] += 1
            else:
                uyariTip[uyari] = 1
        with open("UyariAyristirlmis.txt", "w", encoding="utf-16") as dosya2:#Tarih adlı dosyama ayrıştırdığım verileri yazıyorum
            for uyari, sayi in uyariTip.items():
                dosya2.write(f'{uyari} {sayi} \n')
                print(f"{uyari}: {sayi} adet")
def cizgiGrafik():
    # Matplotlib grafiği oluşturun
    fig = Figure(figsize=(6, 4), dpi=100)
    grafik = fig.add_subplot(111)
    grafik.plot(list(reversed(tarih)), list(reversed(adet)), label='_nolegend_',color='blue')  # Çizgi grafiğinin rengini değiştirme...
    grafik.set_xlabel("Tarih")  # set_xlabel kullanılmalı
    grafik.set_ylabel("SİSTEM LOGLANMA SAYISI")  # set_ylabel kullanılmalı
    grafik.set_title("Sistem Log Meşguliyet Grafiği")  # set_title kullanılmalı
    grafik.set_xticks([tarih[0], tarih[-1]])
    kaydetme_yolu = "static/images/grafik.png"
    # Grafiği images olarak kaydetme...
    fig.savefig(kaydetme_yolu)



powerShellFonksiyon()
tarihAyristirma()
logAyristirma()

#Ayrıştırılmış tarihleri okuyarak listeme ekliyorum ve cizgigrafik fonksiyonuma yolluyorum...
with open("TarihAyristirlmis.txt", "r", encoding="utf-16") as dosya:
    for satir in dosya:
        satir = satir.strip().split()  # Satırı boşluklara göre bölelim
        tarih.append(satir[0])  # İlk kelime tarih
        adet.append(int(satir[1]))  # İkinci kelime adet sayısı

cizgiGrafik()

#Ayrıştırılmış uyari tiplerini listeme ekliyorum ve flask ile web siteme yönlendiriyorum...
with open("UyariAyristirlmis.txt", "r", encoding="utf-16") as dosya2:
    for indeks, satir in enumerate(dosya2):
        if indeks==0:
            continue
        else:
            satir = satir.strip().split()  # Satırı boşluklara göre bölelim
            uyari.append(satir[0]+" "+satir[1])
            adet2.append(int(satir[2]))  # İkinci kelime adet sayısı

bugununLogSayisi=str(adet[0])
dununLogSayisi=str(adet[1])
ortalamahesaplama=veriSayac/gunsayisi
print(f"Ortlama Günlük Log sayisi {ortalamahesaplama}")


#FLASK KISMI
app = Flask(__name__)
@app.route('/')
def AnaSayfa():
    return render_template('anasayfa.html',veriSayac=veriSayac,uyari=uyari,adet2=adet2,bugununLogSayisi=bugununLogSayisi,dununLogSayisi=dununLogSayisi,gunsayisi=gunsayisi)
if __name__ == '__main__':
    app.run(debug=True)


