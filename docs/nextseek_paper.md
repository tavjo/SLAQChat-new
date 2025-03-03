---
article:
  doi: 10.7171/3fc1f5fe.db404124
  elocation-id: nextseek-interopaerable-data-management
  issue: 1
  volume: 33
author:
- Dikshant Pradhan
- Huiming Ding
- Jingzhi Zhu
- Bevin P. Engelward
- Stuart S. Levine
bibliography: /tmp/tmp-52MdUGcl1ilbqr.json
copyright:
  text: Copyright © 2022 Association of Biomolecular Resource
    Facilities. All rights reserved.
  type: Copyright
csl: /app/dist/server/server/utils/citations/citeStyles/american-medical-association.csl
date:
  day: 02
  month: 02
  year: 22
journal:
  publisher-name: Association of Biomolecular Resource Facilities
  title: Journal of Biomolecular Techniques
link-citations: true
title: "NExtSEEK: Extending SEEK for Active Management of Interoperable
  Metadata"
---

# **ABSTRACT**

Data management is a critical challenge required to improve the rigor
and reproducibility of large projects. Adhering to Findable, Accessible,
Interoperable, and Reusable (FAIR) standards provides a baseline for
meeting these requirements. Although many existing repositories handle
data in a FAIR-compliant manner, there are limited tools in the public
domain to handle the metadata burden required to connect data from
multi-omic projects that span multiple institutions and are deposited in
diverse repositories. One promising approach is the SEEK platform, which
allows for diverse metadata and provides an established repository. SEEK
is challenged by the assumption of single deposition events where a
sample is immutable once entered in the database. This is structured for
published data but presents a limitation for ongoing studies where
multiple sequential events may occur in a single sample at different
sites. To address this issue, we have created a modified wrapper around
the SEEK platform that allows for active data management by establishing
more discrete sample types that are mutable to permit the expansion of
the types of metadata, allowing researchers to track additional
information. The use of discrete nodes also converts assays from nodes
to edges, creating a network model of the study and more accurately
representing the experimental process. With these changes to SEEK, users
are able to collect and organize the information that researchers need
to improve reusability and reproducibility as well as make data and
metadata available to the scientific community through public
repositories.

ADDRESS CORRESPONDENCE TO: Stuart Levine, Massachusetts Institute of
Technology, 77 Massachusetts Avenue, Building 68-304D, Cambridge, MA
02139, USA (Phone: 617-452-2949; E-mail:
[slevine\@mit.edu](mailto: slevine@mit.edu "null")).

**Conflict of Interest Disclosures:** The authors declare no conflicts
of interest.

**Keywords:** metadata, data collection, data management

# **INTRODUCTION**

Improving reproducibility and reusability of data generated from large
collaborations is a critical challenge complicated by the variety of
data and sample types that must be tracked and shared. Although
Findable, Accessible, Interoperable, and Reusable (FAIR) standards were
established to facilitate reuse of scientific data[@1059e021] and many
data repositories are FAIR compliant, they are typically built to handle
specific flavors of data.[@80a7532b] Large multi-omics studies
frequently must either split their data across multiple
repositories---making connecting datasets challenging---or create
specific repositories that serve only a single study (eg,
ENCODE[@dec69145]), creating new silos of data. Repositories serve as
final endpoints for data and prioritize collecting metadata about
deposited data and immediately adjacent procedures. Users must complete
all of their experiments and finalize their results prior to deposition,
separating data acquisition and deposition. This temporal separation can
result in the loss of the rich metadata and detailed provenance, which
are necessary in multi-omics studies to assess data quality and
integrate data,[@80a7532b],[@83e3f655] particularly when associated with
significant time or staffing changes. There are few resources available
to handle this metadata, but SEEK is a promising platform that focuses
specifically on metadata collection.[@79bcfe5e] SEEK permits complex
queries of metadata, interoperability with external repositories,
application programming interface access, and controlled access and
permissions, all built around FAIR principles. SEEK also supports
exportation of data and metadata and has an existing public installation
at fairdomhub.org, allowing for broad, non--project-specific public
deposition of metadata.[@5d9e0cd6]

A key limitation of this approach is the focus on the final deposition
of data. Because data collection can occur over years, obtaining
accurate data provenance is a key challenge.[@b4b73ed7] This is
especially true for large multisite collaborations. Samples within SEEK
are assumed to be immutable (ie, deposited only once), which does not
allow for the ongoing collection and updating of information in a
simple, coherent, and organized way. We have developed Network Extended
SEEK (NExtSEEK), a modified wrapper around SEEK that allows for active
data management. We chose to modify SEEK because of its existing
functionality, public installation, open-source and modular code, and
existence of a public repository. We modified SEEK's data model to
prioritize connections between samples and define discrete sample types
that can be freely connected. Sample types in NExtSEEK are mutable to
allow researchers to update sample records and add new metadata as
required. NExtSEEK also allows for sparsity in data matrices, allowing
users to capture only relevant metadata and adhere to the standards of
their repository of choice. Finally, we expanded upon SEEK's ability to
extract sample records from Microsoft Excel sheets to allow for greater
flexibility in data collection. These additions are designed to
facilitate the collection of information alongside the experimental
process, help maintain records through staff turnover, share metadata
with collaborators, and allow for the integration of datasets. Data and
metadata from NExtSEEK are easily exported to the public metadata
repository FAIRDOMHub and can be linked to the disparate repositories
that hold the respective data files.

# **RESULTS AND DISCUSSION**

In the process of implementing a local SEEK instance for gathering
sample and metadata for several large projects, we identified a key
challenge: an individual sample handled by multiple users would result
in a large number of duplicated sample records on the database,
different only slightly by modest changes. For example, a mouse with a
record created at birth would get a new record upon an initial treatment
protocol, another when challenged with a drug, and another at necropsy.
This disconnect between the data records and the physical samples
created a very challenging environment, limiting the ability of users to
identify key data and metadata points for searching and discouraging
reuse by users. Retaining all the protocols separately and uploading a
summary at the end could bypass this issue but would be a significant
challenge to implement.

To address these challenges, we developed a wrapper around the SEEK
architecture, NExtSEEK, which modifies the tool to accommodate sample
mutability and improve data capture while not disrupting the derivative
archival nature of the platform. First, the concept of assays was
modified, moving them from nodes that are parents of samples to the
edges between samples, describing either the update of a sample or the
connections between samples ([Figure 1](#nq045omjv3o)A).[@546d00a5] In
this way, it becomes clear how a physical sample was processed to give
rise to additional samples or datasets. We define assays as experiment
procedures described by protocols. Although SEEK defines assays to be
discrete measurement events (equivalent to experiments), we have
redefined assays to be broad classes, of which experiments are
individual instances, that can connect samples across multiple
experiments and be reused throughout the project ([Figure
1](#nq045omjv3o)B).

![](https://assets.pubpub.org/5i4vkyqj/31642021272966.png){#nq045omjv3o}

NExtSEEK modifications to the SEEK architecture. (*A*) NExtSEEK converts
the hierarchical Investigation/Study/Assay (ISA) model to a network
model by implementing Assays as edges instead of nodes. The top image
represents SEEK architecture and the bottom represents NExtSEEK
architecture. (*B*) In the NExtSEEK network model, experiments are
considered specific instances of Assays. The top image represents SEEK
architecture and the bottom represents NExtSEEK architecture. Yellow
boxes show Assays with example protocols, and green boxes show
individual samples. (*C*) NExtSEEK categorizes sample types as broad
groups identifiable by being possible inputs to shared Assays. An
example is shown of a GAS sample type (including atmospheric air sample)
and a CEX sample type---both lysates and cell culture supernatants. All
samples of both sample types could be subject to mass spectrometry,
resulting in the creation of D.MSP sample types. (*D*) The NExtSEEK
network is a nonhierarchical directed graph. Examples shown are between
MUS and DNA samples with different assays highlighted. CEX, cell
extract; D.MSP, mass spectrometry data; ISA, Investigation/Study/Assay
infrastructure; MUS, murine; TIS, tissue.

Next, samples were allowed to be mutable to capture updates as
alterations to their sample records. To facilitate this mutability, we
added the concept of a Sample Type, of which an individual sample record
is an instance. A Sample Type is a list of all possible metadata
attributes that describe the samples, whether they are populated or not.
Different individual samples are expected to have different metadata as
a result of having been produced by different assays ([Figure
1](#nq045omjv3o)C). Different sample types are delineated by which
assays can generate them and which assays can be performed on them. As
researchers do novel experiments and need to capture new metadata,
additional attributes to sample types can be added. Users can update
sample records with altered or additional metadata as they are affected
by experiments, changes in storage condition, location, and other
factors.

The addition of "hard sample typing" contrasts with the general SEEK
platform, which allows every sample to be a unique type specific to
their experiments. SEEK uses the Just Enough Results Model based on
Minimal Information Models, which define the minimal amount of metadata
that needs to be published with a sample for interoperability and reuse
of metadata.[@5cccb46e] By instead defining hard sample types and
allowing them to be modified as additional information needs to be
collected, NExtSEEK allows for similar samples to be grouped together
for easier browsing, standardized attribute names for understanding
between collaborators, and space to collect the metadata that
repositories or community standards will require
up-front.[@42441245],[@c64f26d6],[@ba5a4471] Sample types are defined to
be broad and allowed to be sparse so that users have the flexibility to
comply with the standards and requirements of the repository of their
choosing. However, because the sample types are not universal, different
projects or installations can have their own sets of sample types,
defined as needed by the project.

To capture detailed provenance, NExtSEEK prioritizes connections between
samples equally to the organization of assays. Typically, SEEK requires
that the definition for a sample type designate its parent types. This
requires anticipating the connections between types and prohibits types
from pointing to themselves, which is often not possible in large
collaborations. NExtSEEK adds the ability for any sample to point to
samples of any other sample type or of the same type as its parent, so
long as an assay can connect them, as seen in [Figure 1](#nq045omjv3o)D.
Users can capture relationships between samples and data as necessary,
with the ability to make novel connections. As researchers do
experiments and generate new samples, their records expand the network
of samples, forming a directed multigraph ([Figure 2](#ni9gd7qypdm)A).
The NExtSEEK data model assumes inheritance of metadata[@dca4f3f2] so
users do not have to upload redundant metadata. For example, the
genotype of the tissues in [Figure 2](#ni9gd7qypdm)A is implicitly
captured, as the tissues are connected to their parent mice, whose
genotypes are explicitly recorded.

![](https://assets.pubpub.org/uqp5krq7/11642021272967.png){#ni9gd7qypdm}

Practical utilization of NExtSEEK for data management and deposition.
(*A*) A network model of sample types in two projects, which are
highlighted as light red and light blue. Sample Types are highlighted in
colors based on inclusion in the projects, and their shape outlines are
based on sample type. Representative sample types are shown. Protocols
used in Assays are indicated in colors based on the group performing the
experiments. (*B*) A deposition of project data from NExtSEEK. The mass
spectrometry dataset deposited in Proteomics IDEntification Database
(PRIDE) collects metadata from multiple sample types in NExtSEEK, which
is highlighted in green. Full metadata are also deposited in FAIRDOMHub,
highlighted in blue, with pointers to the dataset in PRIDE, indicated by
dashed blue lines.  

As samples in large collaborations are handled by multiple researchers,
the information required by data repositories and journals is often
generated by different people at different times. In order to minimize
the delay between data generation and deposition, users require
flexibility in how and when they can upload metadata. SEEK collected
metadata via Sample Sheets, which are templates uniquely defined for
each sample type that users could fill in with their metadata for each
specific experiment. In contrast, by using the concept of defined and
discrete sample types, NExtSEEK instead defines Assay Sheets, which
collect information for specific assays rather than individual samples.
Whereas a SEEK Sample Sheet contained the full list of metadata
attributes for a single experiment, Assay Sheets can span multiple
Sample Types while collecting only specific fields for those Sample
Types as needed (ie, creating a sparse matrix) and while capturing
parent--child relationships. For example, in creating a DNA sample from
an ear punch, an Assay Sheet would include both the mouse and DNA sample
types ([Figure 1](#nq045omjv3o)D). Within the DNA sample metadata, it
would include DNA type, concentration, and volume, whereas metadata
fields for Illumina barcode or plasmid properties (such as selectable
marker) would not be included on the Assay Sheet, as they are irrelevant
for the protocol. Should the resultant DNA be used to create an Illumina
library, the library preparation Assay Sheet would include different
metadata fields, such as Illumina barcode and library preparation kit.
As such, Assay Sheets allow users to upload and update samples in a
manner that fits into their workflow, and individual users only need to
be responsible for the information that they generate.

NExtSEEK is designed around the expectation that data from large
multi-omic projects often will require multiple depositions in several
public repositories. To accomplish this, researchers should identify the
ideal endpoints for their data and samples before the start of data and
metadata collection as well as note the mandatory metadata they need (a
checklist for preparation to use NExtSEEK is available at
<https://github.com/BMCBCC/NExtSEEK>). Assay Sheets can be tailored to
include fields for all information required at deposition. This allows
for a strong maintenance of both data provenance (as information is
collected close to the time of generation) as well as maintaining
field-specific ontologies, which are both requirements of FAIR
principles. Upon completion, a project may span multiple laboratories
and sample types ([Figure 2](#ni9gd7qypdm)A). The NExtSEEK database can
be queried, and the metadata required for deposition will be aggregated
and made available immediately ([Figure 2](#ni9gd7qypdm)B).
Additionally, records can be converted to an Investigation/Study/Assay
(ISA) infrastructure for deposition to FAIRDOMHub, where they can point
to the data deposited in public data repositories.[@128d4b6f] As
research builds on existing sample networks in NExtSEEK, samples may
also belong to multiple projects ([Figure 2](#ni9gd7qypdm)A). Additional
work that builds upon existing samples can be connected to the old
records.

By defining hard sample types that are also mutable and sparse, NExtSEEK
builds a module for active data management around the SEEK platform.
This helps researchers close the gap between data generation and
deposition while navigating the variety of data standards set by
journals and repositories. Collecting information at the point of
generation also helps to preserve rich metadata for better quality
control of samples and data. Because records on NExtSEEK are collected
prior to deposition, users can also store information that is private
and internally useful alongside the key metadata to be published,
supporting limited data sharing for collaborations and maintaining
records through staff turnover. NExtSEEK also preserves relationships
among datasets, key information that is often lost when subtypes of data
are put into different public repositories. The network-based data model
allows users to easily build on existing research and connect new
samples and data to existing records. This maintains provenance of
samples and data, helping researchers aggregate metadata across projects
and collaborations for depositions to public data repositories.
Provenance can be publicly maintained by deposition to FAIRDOMHub, an
open installation of SEEK. Taken together, NExtSEEK greatly facilitates
rendering data FAIR compliant by making data easier to find and more
easily accessible and by providing key information so that data can be
used in a wide range of applications. Together with enhanced capacity
for preserving detailed provenance and metadata information by enabling
collection in real time, NExtSEEK allows researchers to reuse data for
different purposes than originally envisioned, including multi-omics
studies that give rise to novel insights.

# **ACKNOWLEDGMENTS**

The authors thank the members of the IMPAcTB consortium and MIT
Superfund Research Project, particularly Douglas Lauffenburger and Sarah
Fortune, for their contributions to the development of NExtSEEK and
members of the MIT BioMicro Center for their review of the manuscript.
This work was supported by the Koch Institute Support Grant P30-CA14051
from the National Cancer Institute, the MIT Center for Environmental
Health Sciences Support Grant P30-ES002109 from the National Institute
of Environmental Health Sciences, the National Institute of
Environmental Health Sciences Superfund Basic Research Program, National
Institute of Health, P42 ES027707, and National Institutes of Health
contract 75N93019C00071.
