require 'json'

package = JSON.parse(File.read(File.join(__dir__, '..', 'package.json')))

Pod::Spec.new do |s|
  s.name = 'DiaryOneVision'
  s.version = package['version']
  s.summary = 'On-device visual evidence analysis for Diary One'
  s.description = s.summary
  s.license = { :type => 'Proprietary' }
  s.author = 'Nexleap'
  s.homepage = 'https://diary.luxe'
  s.platforms = { :ios => '16.4' }
  s.swift_version = '5.9'
  s.source = { :path => '.' }
  s.static_framework = true
  s.dependency 'ExpoModulesCore'
  s.frameworks = 'Vision', 'UIKit', 'AVFoundation'
  s.pod_target_xcconfig = { 'DEFINES_MODULE' => 'YES' }
  s.source_files = '**/*.{h,m,swift}'
end
