#!/usr/bin/perl
#
# CGI script to create a table of values from RRD
use CGI qw(:all *table *Tr);
use RRDs;
use POSIX qw(strftime);
use POSIX qw(locale_h);

$ENV{'LANG'}='de_DE.UTF-8';
setlocale(LC_TIME, 'de_DE.UTF-8');

# path to database
$rrdb='../../hmc5883-gas-counter/count.rrd';

$query=new CGI;
#$query=new CGI("type=consumweek");

print header(-charset=>"utf-8");

$type=$query->param('type');
if ($type !~ /(count|consum)(day|week|month|year)/) {
  print "Invalid type\n";
  exit;
}
$sensor=$1;
$range=$2;

#print "Sensor: $sensor Range: $range\n";

$timeformat="%a, %d. %b %Y";
$resolution=24*60*60;
if ($range eq 'day') {
  $resolution=60*60;
  $timeformat="%a, %d. %b %Y %H:%M";
}

if ($sensor eq 'count') {
  @indexes = (0);
  @headings = ('Zählerstand');
  $title = "Zähler";
  $factor = 1.0;
  $cf = "LAST";
} elsif ($sensor eq 'consum') {
  @indexes = (1);
  $title = "Verbrauch";
  if ($range eq 'day') {
    $factor = 60.0*60.0; # consumption per hour
    @headings = ('m³/h');
  } else {
    $factor = 60.0*60.0*24; # consumption per day
    @headings = ('m³/d');
  }
  $cf = "AVERAGE";
}


($start,$step,$names,$data) = getdata($rrdb, $cf, $resolution, $range);
# print result

# print heading
$style=<<END;
<!-- 
body {
  font: 10px/16px verdana, arial, helvetica, sans-serif;
  background-color: white;
  color: black;
}
th, td {
  border-width: 1px 1px 0px 0px;
  border-style: solid;
  border-color: #998DB3;
  text-align: right;
  width: 50px;
}
th {
  background-color: lightgreen;
  font-weight: normal;
}
thead {
  position: fixed;
  top: 0px;
  background-color: white;
  z-index: 1;
}
tbody {
  position: absolute;
  top: 30px;
  z-index: -1;
}
.mindata {
  color: blue;
}
.maxdata {
  color: red;
}
.time {
  color: black;
  text-align: left;
  width: 100px;
}
-->
END

print start_html(-title=>"Gasverbrauch - $title", -style=>{-code=>$style});
print start_table();
print "\n";
print thead(Tr(th({-class=>'time'}, $title), th([@headings])));
print "\n";

# print data
for $line (@$data) {
  $hastime=0;

  print start_Tr({-class=>'avrdata'});
  if (! $hastime) {
    print td({-class=>'time'}, strftime($timeformat, localtime($start)));
  }

  print formatline(@$line[@indexes]);
  print end_Tr;
  print "\n";

  $start += $step;
}
print end_table();
print end_html;

sub getdata {
  my ($db, $cf, $resolution, $range) = @_;

  my $sarg = "now -1 $range";
  if ($range eq 'month') {
    $sarg = "now - 30 days";
  }
  my ($start,$step,$names,$data) = RRDs::fetch($db, $cf, '-r', $resolution, '-s', $sarg, '-e', 'now');

  # check error
  my $err=RRDs::error;
  print "$err\n" if $err;
  exit if $err;
  return ($start,$step,$names,$data);
}

sub formatline {
  my @line = @_;
  my $str = '';
  for $val (@line) {
    if (defined $val) {
      $str .= td(sprintf "%5.1f", $val * $factor);
    } else {
      $str .= td;
    }
  }
  return $str;
}