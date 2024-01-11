%global version_id parent
%global upstream_name jmx_exporter
%global simple_client_version 0.6.0

# Filter requires for the Java Agent as deps are shaded within.
%global jmx_or_client io\\.prometheus\\.jmx:.*|io\\.prometheus:simpleclient.*|org\\.yaml:snakeyaml.*
%global mvn_requires_filter .*mvn\\(%{jmx_or_client}\\)
%global java_headless_filter \\(?.*java-headless.*\\)?
%global __requires_exclude ^%{java_headless_filter}|%{mvn_requires_filter}$

Name:           prometheus-jmx-exporter
Version:        0.12.0
Release:        10%{?dist}
Summary:        Prometheus JMX Exporter

License:        ASL 2.0
URL:            https://github.com/prometheus/jmx_exporter/

Source0:        https://github.com/prometheus/jmx_exporter/archive/%{version_id}-%{version}.tar.gz
Patch1:         properly_rewrite_namespace.patch
Patch2:         0001-Fix-CVE-2017-18640-and-add-a-test.patch
Patch3:         0001-Fix-CVE-2022-1471-and-add-a-test.patch

BuildArch:  noarch
Requires: %{name}-jdk-binding
Suggests: %{name}-openjdk11 = %{version}-%{release}

BuildRequires: maven-local
BuildRequires: mvn(org.apache.felix:maven-bundle-plugin)
BuildRequires: mvn(org.apache.maven.plugins:maven-assembly-plugin)
BuildRequires: mvn(org.apache.maven.plugins:maven-shade-plugin)
BuildRequires: mvn(org.yaml:snakeyaml)
BuildRequires: mvn(io.prometheus:simpleclient)
BuildRequires: mvn(io.prometheus:simpleclient_hotspot)
BuildRequires: mvn(io.prometheus:simpleclient_common)
BuildRequires: mvn(io.prometheus:simpleclient_httpserver)

Provides: bundled(io.prometheus.jmx:collector) = %{version}
Provides: bundled(io.prometheus:simpleclient) = %{simple_client_version}
Provides: bundled(org.yaml:snakeyaml) = 1.32
Provides: bundled(biz.source_code:base64coder) = 2010.12.19
Provides: bundled(commons-codec:commons-codec) = 1.11
Provides: bundled(io.prometheus:simpleclient_hotspot) = %{simple_client_version}
Provides: bundled(io.prometheus:simpleclient_httpserver) = %{simple_client_version}
Provides: bundled(io.prometheus:simpleclient_common) = %{simple_client_version}

%description
JMX to Prometheus exporter: a collector that can be configured to scrape
and expose MBeans of a JMX target. This exporter is intended to be run as
a Java Agent, exposing a HTTP server and serving metrics of the local JVM.

%package openjdk8
Summary: OpenJDK 1.8.0 binding for %{name}
Provides: %{name}-jdk-binding = %{version}-%{release}
Conflicts: %{name}-jdk-binding
Requires: %{name} = %{version}-%{release}
Requires: java-1.8.0-headless

%description openjdk8
OpenJDK 1.8.0 binding package for %{name}

%package openjdk11
Summary: OpenJDK 11 binding for %{name}
Provides: %{name}-jdk-binding = %{version}-%{release}
Conflicts: %{name}-jdk-binding
Requires: %{name} = %{version}-%{release}
Requires: java-11-headless

%description openjdk11
OpenJDK 11 binding package for %{name}

%package openjdk17
Summary: OpenJDK 17 binding for %{name}
Provides: %{name}-jdk-binding = %{version}-%{release}
Conflicts: %{name}-jdk-binding
Requires: %{name} = %{version}-%{release}
Requires: java-17-headless

%description openjdk17
OpenJDK 17 binding package for %{name}

%prep
%setup -q -n %{upstream_name}-%{version_id}-%{version}

%patch1 -p1
%patch2 -p1
%patch3 -p1

%pom_remove_plugin org.vafer:jdeb jmx_prometheus_httpserver
%pom_remove_plugin org.apache.maven.plugins:maven-failsafe-plugin jmx_prometheus_javaagent
%pom_remove_plugin org.codehaus.mojo:build-helper-maven-plugin jmx_prometheus_javaagent

# Don't install artefacts from the reactor but the java agent itself. This is because
# the agent needs deps from the reactor but shades them.
%mvn_package "io.prometheus.jmx:jmx_prometheus_httpserver" __noinstall
%mvn_package "io.prometheus.jmx:parent" __noinstall

# Don't depend on obsolete sonatype-oss-parent
# See: https://github.com/prometheus/jmx_exporter/issues/420
%pom_xpath_remove pom:project/pom:parent

%build
# ignore spurious test errors with: -Dmaven.test.failure.ignore=true
%mvn_build -j

%install
%mvn_install

%files -f .mfiles
%license LICENSE
%doc NOTICE

%files openjdk8
# empty files for the binding package

%files openjdk11
# empty files for the binding package

%files openjdk17
# empty files for the binding package

%changelog
* Wed Dec 07 2022 Severin Gehwolf <sgehwolf@redhat.com> - 0.12.0-10
- Bump release.

* Wed Dec 07 2022 Severin Gehwolf <sgehwolf@redhat.com> - 0.12.0-9
- Fix CVE-2022-1471 by using SafeConstructor.

* Mon Sep 26 2022 Jonathan Dowland <jdowland@redhat.com> - 0.12.0-8
- Bump snakeyaml version to 1.32 to collect fix for CVE-2022-25857
  (BZ 2126789)

* Tue Aug 31 2021 Severin Gehwolf <sgehwolf@redhat.com> - 0.12.0-7
- Add JDK binding sub-packages so that the package
  can be used with either JDK 11 or JDK 17.
- Add requirement on base package for the JDK binding packages.

* Mon Apr 20 2020 Severin Gehwolf <sgehwolf@redhat.com> - 0.12.0-6
- Fix CVE-2017-18640 by using updated snakeyaml.

* Wed Oct 09 2019 Severin Gehwolf <sgehwolf@redhat.com> - 0.12.0-5
- rebuilt

* Wed Oct 09 2019 Severin Gehwolf <sgehwolf@redhat.com> - 0.12.0-4
- rebuilt

* Wed Oct 09 2019 Severin Gehwolf <sgehwolf@redhat.com> - 0.12.0-3
- Advertise correct bundled snakeyaml version (1.25)

* Tue Sep 03 2019 Severin Gehwolf <sgehwolf@redhat.com> - 0.12.0-2
- Add patch to properly name-space included dependencies

* Mon Aug 12 2019 Severin Gehwolf <sgehwolf@redhat.com> - 0.12.0-1
- Initial package.

