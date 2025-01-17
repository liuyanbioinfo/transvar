"""
The MIT License

Copyright (c) 2015
The University of Texas MD Anderson Cancer Center
Wanding Zhou, Tenghui Chen, Ken Chen (kchen3@mdanderson.org)

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""

import configparser
import subprocess
import os, sys
from .err import *
from builtins import input

from future.standard_library import install_aliases
install_aliases()
from urllib.request import urlopen
# import urllib.request, urllib.error, urllib.parse

def samtools_faidx(fn):
    ## samtools_path='%s/samtools' % os.path.abspath(os.path.dirname(__file__))
    samtools_path = 'samtools'
    err_print("Faidx indexing")
    ## requires samtools here
    subprocess.check_call([samtools_path, 'faidx', fn])

def gunzip(fn):

    if not fn.endswith('.gz'):
        err_die('Target file %s not ends with .gz' % fn)

    import gzip
    f_out = open(fn[:-3], 'wt')
    f_in = gzip.open(fn, 'rt')
    f_out.writelines(f_in)
    f_in.close()
    f_out.close()
    os.remove(fn)

class CustomConfigParser(configparser.RawConfigParser):
    def read(self, filenames, encoding=None):
        """
        重写 `read` 方法，在读取配置文件后，自动解析并修正其中的相对路径。
        
        参数：
        filenames (str | list): 配置文件路径，可以是字符串或路径列表。
        encoding (str): 可选的文件编码方式。
        """
        # 调用父类的 read 方法
        super().read(filenames, encoding)

        # 获取配置文件的绝对路径并解析相对路径
        if isinstance(filenames, list):
            # 如果是文件列表，选择第一个文件作为参考路径
            config_file_path = os.path.abspath(filenames[0])
        else:
            config_file_path = os.path.abspath(filenames)

        # 修改配置中的相对路径为绝对路径
        for section in self.sections():
            for key in self.options(section):
                value = self.get(section, key)
                # 跳过refversion
                if key == "refversion":
                    continue
                if value and (value.startswith('./') or not os.path.isabs(value)):
                    # 获取配置文件所在的目录，并将相对路径转为绝对路径
                    abs_value = os.path.join(os.path.dirname(config_file_path), value)
                    self.set(section, key, abs_value)

cfg_fns = [
    os.path.expanduser(os.getenv('TRANSVAR_CFG', 
                                 os.path.join(os.path.dirname(__file__), 'transvar.cfg'))),
    os.path.expanduser('~/.transvar.cfg')]

downloaddirs = [
    os.path.expanduser(os.getenv('TRANSVAR_DOWNLOAD_DIR',
                                 os.path.join(os.path.dirname(__file__), 'transvar.download'))),
    os.path.expanduser('~/.transvar.download')]

dwroot = 'https://zhouserver.research.chop.edu/TransVar/annotations/'
## the following are obsolete
## dwroot = 'http://zwdzwd.io/transvar_user/annotations/'
## dwroot = 'https://dl.dropboxusercontent.com/u/6647241/annotations/'

## the following will become obsolete in a year
# dwroot = 'http://transvar.info/transvar_user/annotations/'

fns = {}

##############################
## "raw" section
## raw transcript tables
##############################

# download link updates:
# 03/06/2016: ftp://ftp.ncbi.nlm.nih.gov/genomes/H_sapiens/ARCHIVE/ANNOTATION_RELEASE.105/GFF/ref_GRCh37.p13_top_level.gff3.gz
# 01/01/2015: https://dl.dropboxusercontent.com/u/6647241/annotations/hg19.map?dl=1'
fns[('hg19', 'raw')] = [
    ('raw_refseq', 'hg19.refseq.gff.gz',
     'ftp://ftp.ncbi.nlm.nih.gov/genomes/H_sapiens/ARCHIVE/ANNOTATION_RELEASE.105/GFF/ref_GRCh37.p13_top_level.gff3.gz'),
    ('raw_ccds', 'hg19.ccds.txt',
     'ftp://ftp.ncbi.nlm.nih.gov/pub/CCDS/archive/Hs37.3/CCDS.current.txt'),
    ('raw_ensembl', 'hg19.ensembl.gtf.gz',
     'ftp://ftp.ensembl.org/pub/release-75/gtf/homo_sapiens/Homo_sapiens.GRCh37.75.gtf.gz'),
    ('raw_gencode', 'hg19.gencode.gtf.gz',
     'ftp://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_19/gencode.v19.annotation.gtf.gz'),
    ('raw_ucsc', 'hg19.ucsc.txt.gz',
     '%s/hg19.ucsc.refgene.txt.gz' % dwroot),
    ('raw_aceview', 'hg19.aceview.gff.gz',
     'ftp://ftp.ncbi.nih.gov/repository/acedb/ncbi_37_Aug10.human.genes/AceView.ncbi_37.genes_gff.gff.gz'),
    ('raw_known_gene', 'hg19.knowngene.gz',
     '%s/UCSC_knownGene_hg19.gz?dl=1' % dwroot),
    (None, 'hg19.knowngene_alias.gz', '%s/UCSC_kgAlias.gz?dl=1' % dwroot),
]

# download link update:
# 01/05/2015: refseq: ftp://ftp.ncbi.nlm.nih.gov/genomes/H_sapiens/GFF/ref_GRCh38.p2_top_level.gff3.gz
# 01/05/2015: ensembl: ftp://ftp.ensembl.org/pub/release-77/gtf/homo_sapiens/Homo_sapiens.GRCh38.77.gtf.gz
# 06/27/2016: refseq: ftp://ftp.ncbi.nlm.nih.gov/genomes/H_sapiens/GFF/ref_GRCh38.p7_top_level.gff3.gz
# 06/27/2016: ensembl: ftp://ftp.ensembl.org/pub/release-84/gtf/homo_sapiens/Homo_sapiens.GRCh38.84.gtf.gz
# 06/27/2016: gencode: ftp://ftp.sanger.ac.uk/pub/gencode/Gencode_human/release_21/gencode.v21.annotation.gtf.gz
# 01/21/2019: ccds: ftp://ftp.ncbi.nlm.nih.gov/pub/CCDS/current_human/CCDS.current.txt
# 03/14/2019: refseq: ftp://ftp.ncbi.nlm.nih.gov/genomes/H_sapiens/GFF/ref_GRCh38.p12_top_level.gff3.gz
# 03/14/2019: gencode: ftp://ftp.sanger.ac.uk/pub/gencode/Gencode_human/release_24/gencode.v24.annotation.gtf.gz
# 03/14/2019: ensembl: ftp://ftp.ensembl.org/pub/release-84/gtf/homo_sapiens/Homo_sapiens.GRCh38.84.gtf.gz
# 12/04/2019: refseq: ftp://ftp.ncbi.nlm.nih.gov/genomes/Homo_sapiens/current/GCF_000001405.39_GRCh38.p13/GCF_000001405.39_GRCh38.p13_genomic.gff.gz
fns[('hg38', 'raw')] = [
    ('raw_refseq', 'hg38.refseq.gff.gz',
    'ftp://ftp.ncbi.nlm.nih.gov/genomes/H_sapiens/GFF/ref_GRCh38.p12_top_level.gff3.gz'),
    ('raw_ccds', 'hg38.ccds.txt',
     'ftp://ftp.ncbi.nlm.nih.gov/pub/CCDS/archive/22/CCDS.20180614.txt'),
    ('raw_ensembl', 'hg38.ensembl.gtf.gz',
     'ftp://ftp.ensembl.org/pub/release-95/gtf/homo_sapiens/Homo_sapiens.GRCh38.95.gtf.gz'),
    ('raw_gencode', 'hg38.gencode.gtf.gz',
     'ftp://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_29/gencode.v29.annotation.gtf.gz'),
    ('raw_ucsc', 'hg38.ucsc.txt.gz',
     '%s/hg38.ucsc.refgene.txt.gz?dl=1' % dwroot),
]

# download link update:
# 03/14/2019: gencode: ftp://ftp.sanger.ac.uk/pub/gencode/Gencode_mouse/release_M4/gencode.vM4.annotation.gtf.gz from GRCm38.p3 genome
# 03/14/2019: gencode: ftp://ftp.ensembl.org/pub/release-79/gtf/mus_musculus/Mus_musculus.GRCm38.79.gtf.gz
# 03/14/2019: refseq: ftp://ftp.ncbi.nlm.nih.gov/genomes/M_musculus/GFF/ref_GRCm38.p3_top_level.gff3.gz
fns[('mm10', 'raw')] = [
    ('raw_refseq', 'mm10.refseq.gff.gz',
     'ftp://ftp.ncbi.nlm.nih.gov/genomes/M_musculus/GFF/ref_GRCm38.p4_top_level.gff3.gz'),
    ('raw_ccds', 'mm10.ccds.txt',
     'ftp://ftp.ncbi.nlm.nih.gov/pub/CCDS/archive/Mm38.1/CCDS.current.txt'),
    ('raw_ensembl', 'mm10.ensembl.gtf.gz',
     'ftp://ftp.ensembl.org/pub/release-95/gtf/mus_musculus/Mus_musculus.GRCm38.95.gtf.gz'),
    ('raw_gencode', 'mm10.gencode.gtf.gz',
     'ftp://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_mouse/release_M20/gencode.vM20.annotation.gtf.gz'), 
]

## no more support for hg18
# fns[('hg18', 'raw')] = [
#     ('raw_refseq', 'hg18.refseq.gff.gz',
#      'ftp://ftp.ncbi.nlm.nih.gov/genomes/H_sapiens/ARCHIVE/BUILD.36.3/GFF/ref_NCBI36_top_level.gff3.gz'),
#     ('raw_ccds', 'hg18.ccds.txt',
#      'ftp://ftp.ncbi.nlm.nih.gov/pub/CCDS/archive/Hs36.3/CCDS.20090327.txt'),
#     # the AceView hg18 version is deprecated.
#     # ('aceview', 'hg18.aceview.gff.gz',
#     # 'ftp://ftp.ncbi.nih.gov/repository/acedb/ncbi_36_Apr07.human.genes/AceView.ncbi_36.genes_gff.tar.gz'),
#     ('raw_gencode', 'hg18.gencode.gtf.gz',
#      'ftp://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_3c/gencode.v3c.annotation.NCBI36.gtf.gz'),
#     # 'ftp://ftp.sanger.ac.uk/pub/gencode/Gencode_human/release_3c/gencode.v3c.annotation.NCBI36.gtf.gz')
#     ('raw_ucsc', 'hg18.ucsc.txt.gz',
#      '%s/hg18.ucsc.refgene.txt.gz?dl=1' % dwroot),
#     ('raw_ensembl', 'hg18.ensembl.gtf.gz',
#      'ftp://ftp.ensembl.org/pub/release-54/gtf/homo_sapiens/Homo_sapiens.NCBI36.54.gtf.gz'),
# ]

## no more support for mm9
# # download link update:
# # 03/14/2019: gencode: ftp://ftp.sanger.ac.uk/pub/gencode/Gencode_mouse/release_M1/gencode.vM1.annotation.gtf.gz
fns[('mm9', 'raw')] = [
    ('raw_ensembl', 'mm9.ensembl.gtf.gz',
     'ftp://ftp.ensembl.org/pub/release-67/gtf/mus_musculus/Mus_musculus.NCBIM37.67.gtf.gz'),
    ('raw_ccds', 'mm9.ccds.txt',
     'ftp://ftp.ncbi.nlm.nih.gov/pub/CCDS/archive/Mm37.1/CCDS.current.txt'),
    ('raw_gencode', 'mm9.gencode.gtf.gz',
     'ftp://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_mouse/release_M1/gencode.vM1.annotation.gtf.gz'),
]

##############################
## "reference" section
##############################

for rv in ['hg19', 'hg38', 'mm9', 'mm10']:
    fns[(rv,'reference')] = [
        ('reference', '%s.fa' % rv, '%s/%s.fa' % (dwroot, rv)),
        (None, '%s.fa.fai' % rv, '%s/%s.fa.fai' % (dwroot, rv)),
    ]


##############################
## "dbsnp" section
##############################
# ftp://ftp.ncbi.nlm.nih.gov/snp/organisms/human_9606_b146_GRCh37p13/VCF/00-All.vcf.gz
# ftp://ftp.ncbi.nlm.nih.gov/snp/organisms/human_9606_b146_GRCh37p13/VCF/00-All.vcf.gz.tbi
fns[('hg19', 'dbsnp')] = [
    ('dbsnp', 'hg19_dbsnp.vcf.gz', '%s/hg19_dbsnp.vcf.gz' % dwroot),
    (None, 'hg19_dbsnp.vcf.gz.tbi', '%s/hg19_dbsnp.vcf.gz.tbi' % dwroot),
]

##############################
## "anno" section
## indexed transcript tables
##############################
# every (refversion, raw) should have a (refversion, anno)
fns2 = []
for (refv, topic), vs in fns.items():
    if topic == 'raw':          # convert all the raw files
        vs2 = []
        for k, fn, url in vs:
            if k is None:
                continue
            k = k.replace("raw_","")
            afn = fn+'.transvardb'
            vs2.append((k, afn, dwroot+afn))
            afn = fn+'.transvardb.gene_idx'
            vs2.append((None, afn, dwroot+afn))
            afn = fn+'.transvardb.trxn_idx'
            vs2.append((None, afn, dwroot+afn))
            afn = fn+'.transvardb.loc_idx'
            vs2.append((None, afn, dwroot+afn))
            afn = fn+'.transvardb.loc_idx.tbi'
            vs2.append((None, afn, dwroot+afn))
            # if (k.find('knowngene')>=0 or k.find('refseq')>=0 or k.find('gencode')>=0 or k.find('ensembl')>=0):
            for idmap_name in ['protein_id', 'gene_id', 'GeneID','HGNC']:
                afn = fn+'.transvardb.'+idmap_name+'.idmap_idx'
                vs2.append((None, afn, dwroot+afn))
            # afn = fn+'.transvardb.alias_idx'
            # vs2.append((None, afn, dwroot+afn))

        fns2.append(((refv, 'anno'), vs2))

for k, v in fns2:
    fns[k] = v

#######################
## Download utilities
#######################

def download_url(url, file_name):

    import ssl
    # file_name = url.split('/')[-1]
    # try:
    if hasattr(ssl, '_create_unverified_context'):
        u = urlopen(url, context=ssl._create_unverified_context())
    else:
        u = urlopen(url)

    # except urllib2.URLError:
    # return
    f = open(file_name, 'wb')
    meta = u.info()
    raw_file_size = int(meta.get_all("Content-Length")[0])
    file_size = raw_file_size / (1024.0 * 1024.0)
    # err_print("downloading %s (%1.1f MB)" % (file_name, file_size))

    file_size_dl = 0
    block_sz = 8192*2
    sys.stdout.write('[downloading] %s ...' % (file_name, ))
    sys.stdout.flush()
        
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        f.write(buffer)
        # status = r"downloaded %s (%1.1f MB) %10d [%3.2f%%]\033\[K" % (file_name, file_size, file_size_dl, file_size_dl * 100. / raw_file_size)
        # status = status + chr(8)*(len(status)+1)
        progress = float(file_size_dl)/raw_file_size

    print('Done (%1.1f MB).' % (file_size_dl/1000000., ))
    f.close()

def download_requests(url, file_name):

    """ sometimes, urllib2 doesn't work, try requests """
    import requests
    r = requests.get(url, stream=True)
    if r.status_code != 404:
        sys.stdout.write('[bakdownloading] %s ...' % (file_name, ))
        sys.stdout.flush()
        with open(file_name,'wb') as fd:
            n = 0
            
            for chunk in r.iter_content(10000000):
                n += len(chunk)
                fd.write(chunk)

        print('Done (%1.1f MB).' % (n/1000000., ))

def config_set(config, section, option, value):

    if section != 'DEFAULT' and not config.has_section(section):
        config.add_section(section)
    config.set(section, option, value)

def _download_(config, section, fns):

    for pdir in downloaddirs:
        # pdir = os.path.join(os.path.dirname(__file__), 'download')

        if not os.path.exists(pdir):
            try:
                os.makedirs(pdir)
            except:
                continue

        for k, fn, url in fns:
            fnn = os.path.join(pdir, fn)
            
            success = True
            try:
                download_url(url, fnn)
                if k:
                    config_set(config, section, k, fnn)
            except:
                if not fn.endswith('alias_idx'): # sometimes some alias_idx will be missing
                    success = False

            if success:
                continue

            try:                # not quite necessary in most cases, but in some situations, urllib won't work
                download_requests(url, fnn)
                if k:
                    config_set(config, section, k, fnn)
            except:
                # ID mapping is not essential and likely
                # missing for many databases
                if url.endswith('.idmap_idx'):
                    continue
                err_warn('file not available: %s or target directory not found' % url)

        break
    return pdir

def download_idmap(config):
    # 'https://dl.dropboxusercontent.com/u/6647241/annotations/HUMAN_9606_idmapping.dat.gz?dl=1'
    # original ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/idmapping/by_organism/HUMAN_9606_idmapping.dat.gz
    fns = [('uniprot', 'uniprot.idmap_idx',
            '%s/uniprot.idmapping.txt.gz.idx' % dwroot)]
    _download_(config, 'idmap', fns)

def getrv(args, config):

    if args.refversion != 'DEFAULT':
        rv = args.refversion
    elif 'refversion' in config.defaults():
        rv = config.get('DEFAULT', 'refversion')
    else:
        rv = 'hg19'

    return rv

def download_topic(args, config, topic):

    rv = getrv(args, config)
    if (rv, topic) in fns:
        config.set('DEFAULT', 'refversion', rv)
        _download_(config, rv, fns[(rv, topic)])
    else:
        err_die('no pre-built %s for %s, please build manually' % (topic, rv))


def download_anno_topic_ensembl(args, config):

    from ftplib import FTP
    rv = getrv(args, config)
    eshost = 'ftp.ensembl.org'
    ftp = FTP(eshost)
    ftp.login()

    esroot = 'pub/release-%s/' % args.ensembl_release
    if args.refversion == 'DEFAULT':
        species = [os.path.basename(o) for o in ftp.nlst("%s/gtf/" % esroot)]
        for i, sp in enumerate(species):
            err_print('[%d] %s' % (i,sp))
        choice = input("Please choose your target taxon [%d]: " % species.index("homo_sapiens"))
        if not choice:
            choice = species.index('homo_sapiens')
        choice = int(choice)
        err_print("Preparing genomes and annotations for [%d] %s." % (choice, species[choice]))
        if int(choice) <= 0 or int(choice) >= len(species):
            err_die("Invalid choice.")
        rv = species[choice]
    
    esfasta = '%s/fasta/%s/dna/' % (esroot, rv.lower())
    genomes = [fn for fn in ftp.nlst(esfasta) if fn.endswith('dna.toplevel.fa.gz')]
    assert(len(genomes) == 1)
    genome = genomes[0]
    genoname = os.path.basename(genome)
    genodir = _download_(config, rv, [(None, genoname, 'ftp://'+eshost+'/'+genome)])

    esgtf = '%s/gtf/%s' % (esroot, rv.lower())
    gtfs = [fn for fn in ftp.nlst(esgtf) if fn.endswith('gtf.gz')]
    assert(len(gtfs)==1)
    gtf = gtfs[0]
    gtfname = os.path.basename(gtf)
    gtfdir = _download_(config, rv, [(None, gtfname, 'ftp://'+eshost+'/'+gtf)])
    
    err_print("Unzipping genome")
    gunzip(genodir+'/'+genoname)

    samtools_faidx(genodir+'/'+genoname[:-3])
    config_set(config, rv, 'reference', genodir+'/'+genoname[:-3])

    err_print("Indexing GTF")
    from . import localdb
    db = localdb.EnsemblDB()
    db.index([gtfdir+'/'+gtfname])
    config_set(config, rv, 'ensembl', gtfdir+'/'+gtfname+'.transvardb')

    config.set('DEFAULT', 'refversion', rv)

def read_config():
    config = CustomConfigParser()
    config.read(cfg_fns)
    return config

def print_current(args):

    config = CustomConfigParser()
    config.read(cfg_fns)

    print("Configuration files to search:")
    for cfg_fn in cfg_fns:
        print(' - %s' % cfg_fn)
    print('')

    print('Download path:')
    for downloaddir in downloaddirs:
        print(' - %s' % downloaddir)
    print('')
    
    if args.refversion != 'DEFAULT':
        rv = args.refversion
    elif 'refversion' in config.defaults():
        rv = config.get('DEFAULT', 'refversion')
    else:
        err_die("no default reference version set.")

    print("Reference version: %s" % rv)
    if (not config.has_section(rv)):
        print("There is no reference and database set for %s." % rv)
        return

    if 'reference' in config.options(rv):
        print('Reference: %s' % config.get(rv, 'reference'))
    print('')

    print("Available databases: ")
    for op in config.options(rv):
        if op not in ['refversion', 'reference']:
            print(' - %s: %s' % (op, config.get(rv, op)))
            import glob
            idmap_fns = glob.glob(config.get(rv, op) + '*.idmap_idx')
            for idmap_fn in idmap_fns:
                idmap_name = os.path.splitext(idmap_fn.replace(
                    '.idmap_idx',''))[1][1:]
                print('     [idmap] %s - %s' % (idmap_name, idmap_fn))

    return

def main_config(args):


    config = CustomConfigParser()
    config.read(cfg_fns)
    config_altered = False

    if args.k and args.v:
        config_altered = True
        if args.k == 'refversion':
            sec = 'DEFAULT'
        else:
            sec = getrv(args, config)
        config_set(config, sec, args.k, args.v)
        if args.refversion != 'DEFAULT':
            config.set('DEFAULT', 'refversion', args.refversion)

    if args.switch_build is not None:
        if config.has_section(args.switch_build):
            config_altered = True
            config.set('DEFAULT', 'refversion', args.switch_build)
        else:
            err_die("""Build %s is not locally available. Consider
$ tranvar config --download_anno %s""" % (args.switch_build, args.switch_build))

    if args.download_ref:
        config_altered = True
        download_topic(args, config, 'reference')
        if args.refversion != 'DEFAULT':
            config.set('DEFAULT', 'refversion', args.refversion)

    if args.download_anno:
        config_altered = True
        download_topic(args, config, 'anno')
        if args.refversion != 'DEFAULT':
            config.set('DEFAULT', 'refversion', args.refversion)

        # check to make sure reference is also there.
        rv = getrv(args, config)
        if (not args.skip_reference) and (not (config.has_section(rv) and config.has_option(rv, 'reference'))):
            fa_path = input("Please specify fa-indexed fasta of reference (Enter to skip): ")
            fa_path = os.path.expanduser(fa_path)
            if fa_path == '': 
                print("""
Need fa-indexed fasta of reference. You can either download reference through:
$ transvar config --download_ref
or specify through
$ transvar config -k reference -v [path_to_fa] --refversion [build_name]
""")
            else:
                if not os.path.exists(fa_path):
                    err_die("Path %s is non-existent." % fa_path)
                config.set(rv, 'reference', fa_path)

    if args.download_ensembl:
        config_altered = True
        download_anno_topic_ensembl(args, config)
        if args.refversion != 'DEFAULT':
            config.set('DEFAULT', 'refversion', args.refversion)

    if args.download_raw:
        config_altered = True
        download_topic(args, config, 'raw')
        if args.refversion != 'DEFAULT':
            config.set('DEFAULT', 'refversion', args.refversion)
            
    if args.download_dbsnp:
        config_altered = True
        download_topic(args, config, 'dbsnp')
        if args.refversion != 'DEFAULT':
            config.set('DEFAULT', 'refversion', args.refversion)
        
    if args.download_idmap:     # general idmap not pre-made to depend on a particular design
        config_altered = True
        download_idmap(config)
        if args.refversion != 'DEFAULT':
            config.set('DEFAULT', 'refversion', args.refversion)

    if config_altered:
        for cfg_fn in cfg_fns:
            try:
                config.write(open(cfg_fn,'w'))
                break
            except IOError as e:
                pass
    else:
        print_current(args)



